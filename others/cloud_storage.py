import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from pathlib import Path

class CloudStorage:
    """Manages cloud storage operations for MenoCare"""
    
    def __init__(self):
        """Initialize cloud storage manager"""
        self.storage_dir = Path("cloud_storage")
        self.storage_dir.mkdir(exist_ok=True)
        
        # Initialize storage paths
        self.health_records_path = self.storage_dir / "health_records.json"
        self.feedback_path = self.storage_dir / "feedback.json"
        self.user_data_path = self.storage_dir / "user_data.json"
        
        # Set up logging
        logging.basicConfig(
            filename=self.storage_dir / 'cloud_operations.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Initialize storage
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage with default data if needed"""
        # Create health records storage
        if not self.health_records_path.exists():
            self._save_json(self.health_records_path, {"records": []})
        
        # Create feedback storage
        if not self.feedback_path.exists():
            self._save_json(self.feedback_path, {"feedback": []})
        
        # Create user data storage
        if not self.user_data_path.exists():
            default_user = {
                "user_id": "default_user",
                "name": "Jane Doe",
                "age": 52,
                "menopause_stage": "Mid Stage",
                "last_update": datetime.now().strftime("%Y-%m-%d")
            }
            self._save_json(self.user_data_path, default_user)
    
    def _save_json(self, path: Path, data: dict):
        """Save data to JSON file"""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Saved data to {path}")
    
    def _load_json(self, path: Path) -> dict:
        """Load data from JSON file"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"File not found: {path}")
            return {}
    
    def save_health_record(self, record: Dict[str, Any]):
        """Save health record to cloud storage"""
        records = self._load_json(self.health_records_path)
        records["records"].append(record)
        self._save_json(self.health_records_path, records)
        logging.info(f"Saved health record for date: {record.get('date')}")
    
    def get_health_records(self) -> list:
        """Retrieve all health records"""
        data = self._load_json(self.health_records_path)
        return data.get("records", [])
    
    def save_feedback(self, feedback: Dict[str, Any]):
        """Save feedback to cloud storage"""
        feedback_data = self._load_json(self.feedback_path)
        feedback_data["feedback"].append(feedback)
        self._save_json(self.feedback_path, feedback_data)
        logging.info(f"Saved feedback for date: {feedback.get('date')}")
    
    def get_feedback_history(self) -> list:
        """Retrieve feedback history"""
        data = self._load_json(self.feedback_path)
        return data.get("feedback", [])
    
    def update_user_data(self, user_data: Dict[str, Any]):
        """Update user data in cloud storage"""
        current_data = self._load_json(self.user_data_path)
        current_data.update(user_data)
        current_data["last_update"] = datetime.now().strftime("%Y-%m-%d")
        self._save_json(self.user_data_path, current_data)
        logging.info("Updated user data")
    
    def get_user_data(self) -> dict:
        """Retrieve user data"""
        return self._load_json(self.user_data_path)
