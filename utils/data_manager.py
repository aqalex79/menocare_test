import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import os
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from dataclasses import dataclass, asdict
import logging

@dataclass
class HealthRecord:
    """Health record data structure"""
    date: str
    mood: Dict[str, Any]  # score, triggers, notes
    sleep: Dict[str, Any]  # hours, quality, issues
    diet: Dict[str, Any]   # meals, water_intake, supplements
    symptoms: Dict[str, Any]  # physical, emotional, intensity
    exercise: Dict[str, Any]  # type, duration, intensity
    
    def to_dict(self):
        return asdict(self)

class DataManager:
    """Manages all data operations for MenoCare"""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize DataManager with data directory"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize paths
        self.user_data_path = self.data_dir / "user_data.json"
        self.health_records_path = self.data_dir / "health_records.json"
        self.feedback_path = self.data_dir / "feedback_history.json"
        
        # Initialize data storage
        self._initialize_storage()
        
        # Set up logging
        logging.basicConfig(
            filename=self.data_dir / 'data_operations.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def _initialize_storage(self):
        """Initialize data storage files if they don't exist"""
        # User data template
        user_data_template = {
            "user_id": "default_user",
            "name": "Jane Doe",
            "age": 52,
            "menopause_stage": "Mid Stage",
            "height": 163,
            "weight": 58,
            "start_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Create files if they don't exist
        if not self.user_data_path.exists():
            self._save_json(self.user_data_path, user_data_template)
        
        if not self.health_records_path.exists():
            self._save_json(self.health_records_path, {"records": []})
        
        if not self.feedback_path.exists():
            self._save_json(self.feedback_path, {"feedback": []})
    
    def _save_json(self, path: Path, data: dict):
        """Save data to JSON file"""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_json(self, path: Path) -> dict:
        """Load data from JSON file"""
        with open(path, 'r') as f:
            return json.load(f)
    
    def get_user_profile(self) -> dict:
        """Get user profile data"""
        return self._load_json(self.user_data_path)
    
    def update_user_profile(self, data: dict):
        """Update user profile data"""
        current_data = self.get_user_profile()
        current_data.update(data)
        self._save_json(self.user_data_path, current_data)
        logging.info(f"Updated user profile: {data.keys()}")
    
    def save_daily_record(self, record: HealthRecord):
        """Save daily health record"""
        records = self._load_json(self.health_records_path)
        records["records"].append(record.to_dict())
        self._save_json(self.health_records_path, records)
        logging.info(f"Saved health record for date: {record.date}")
        
        # Trigger feedback generation
        self.generate_feedback(record)
    
    def get_health_records(self, days: int = 7) -> List[dict]:
        """Get health records for the specified number of days"""
        records = self._load_json(self.health_records_path)["records"]
        if not records:
            return []
        
        # Convert records to DataFrame for easier filtering
        df = pd.DataFrame(records)
        df['date'] = pd.to_datetime(df['date'])
        
        # Get recent records
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        mask = (df['date'] >= start_date.strftime("%Y-%m-%d"))
        recent_records = df[mask].to_dict('records')
        
        return recent_records
    
    def generate_feedback(self, current_record: HealthRecord):
        """Generate and save feedback based on current and historical data"""
        recent_records = self.get_health_records()
        feedback = {
            "date": current_record.date,
            "analysis": {
                "mood_trend": self._analyze_mood_trend(recent_records),
                "sleep_quality": self._analyze_sleep_quality(recent_records),
                "symptom_changes": self._analyze_symptoms(recent_records),
                "recommendations": self._generate_recommendations(recent_records, current_record)
            }
        }
        
        # Save feedback
        feedback_history = self._load_json(self.feedback_path)
        feedback_history["feedback"].append(feedback)
        self._save_json(self.feedback_path, feedback_history)
        logging.info(f"Generated feedback for date: {current_record.date}")
    
    def get_latest_feedback(self) -> dict:
        """Get the most recent feedback"""
        feedback_history = self._load_json(self.feedback_path)
        if feedback_history["feedback"]:
            return feedback_history["feedback"][-1]
        return {}
    
    def _analyze_mood_trend(self, records: List[dict]) -> dict:
        """Analyze mood trends from records"""
        if not records:
            return {"trend": "Not enough data", "score": 0}
        
        mood_scores = [record['mood']['score'] for record in records]
        return {
            "trend": "improving" if len(mood_scores) > 1 and mood_scores[-1] > mood_scores[0] else "stable",
            "score": sum(mood_scores) / len(mood_scores)
        }
    
    def _analyze_sleep_quality(self, records: List[dict]) -> dict:
        """Analyze sleep quality from records"""
        if not records:
            return {"quality": "No data", "average_hours": 0}
        
        sleep_hours = [record['sleep']['hours'] for record in records]
        sleep_quality = [record['sleep']['quality'] for record in records]
        
        return {
            "quality": sum(sleep_quality) / len(sleep_quality),
            "average_hours": sum(sleep_hours) / len(sleep_hours)
        }
    
    def _analyze_symptoms(self, records: List[dict]) -> dict:
        """Analyze symptom changes from records"""
        if not records:
            return {"changes": "No data", "severity": "Unknown"}
        
        # Extract symptom data
        latest = records[-1]['symptoms']
        
        return {
            "current_severity": latest,
            "trend": self._calculate_symptom_trend(records)
        }
    
    def _calculate_symptom_trend(self, records: List[dict]) -> str:
        """Calculate trend in symptoms"""
        if len(records) < 2:
            return "Not enough data"
        
        first = records[0]['symptoms']
        last = records[-1]['symptoms']
        
        # Compare severity levels
        total_change = sum(last.values()) - sum(first.values())
        if total_change < 0:
            return "improving"
        elif total_change > 0:
            return "worsening"
        return "stable"
    
    def _generate_recommendations(self, records: List[dict], current: HealthRecord) -> List[str]:
        """Generate personalized recommendations based on data"""
        # This would typically interface with Gemini API
        # For now, return basic recommendations
        recommendations = []
        
        mood_trend = self._analyze_mood_trend(records)
        if mood_trend["score"] < 7:
            recommendations.append("Consider daily meditation or light exercise to improve mood")
        
        sleep_data = self._analyze_sleep_quality(records)
        if sleep_data["average_hours"] < 7:
            recommendations.append("Aim for 7-8 hours of sleep. Establish a regular bedtime routine")
        
        symptoms = self._analyze_symptoms(records)
        if symptoms["trend"] == "worsening":
            recommendations.append("Schedule a check-up with your healthcare provider")
        
        return recommendations

    def get_dashboard_data(self) -> dict:
        """Get data for dashboard display"""
        return {
            "user": self.get_user_profile(),
            "recent_records": self.get_health_records(),
            "latest_feedback": self.get_latest_feedback(),
            "health_score": self._calculate_health_score()
        }
    
    def _calculate_health_score(self) -> int:
        """Calculate overall health score"""
        records = self.get_health_records(days=7)
        if not records:
            return 70  # Default score
        
        # Calculate score based on various factors
        mood_score = self._analyze_mood_trend(records)["score"]
        sleep_data = self._analyze_sleep_quality(records)
        symptom_data = self._analyze_symptoms(records)
        
        # Weighted average of different factors
        score = (
            mood_score * 0.3 +
            sleep_data["quality"] * 0.3 +
            (10 - float(sum(symptom_data["current_severity"].values())) / len(symptom_data["current_severity"])) * 0.4
        ) * 10
        
        return round(max(0, min(100, score)))  # Ensure score is between 0 and 100
