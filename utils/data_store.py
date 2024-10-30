import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any

class DataStore:
    """Central data management for MenoCare"""
    
    @staticmethod
    def get_initial_mock_data() -> List[Dict[str, Any]]:
        """Generate initial mock data"""
        end_date = datetime.now() - timedelta(days=1)
        start_date = end_date - timedelta(days=30)
        return DataStore.generate_realistic_data(start_date, end_date)

    @staticmethod
    def initialize_session_state():
        """Initialize all necessary session state variables"""
        if 'user_data' not in st.session_state:
            st.session_state.user_data = {
                "name": "Jane Doe",
                "age": 52,
                "menopause_stage": "Mid Stage",
                "last_update": datetime.now().strftime("%Y-%m-%d")
            }
        
        if 'health_records' not in st.session_state:
            st.session_state.health_records = DataStore.get_initial_mock_data()

    @staticmethod
    def get_data_for_period(period: str = 'week') -> pd.DataFrame:
        """Get data for specified time period"""
        if not st.session_state.health_records:
            return pd.DataFrame()
        
        # Create a new DataFrame instead of using a view
        df = pd.DataFrame(st.session_state.health_records).copy()
        df['date'] = pd.to_datetime(df['date'])
        
        end_date = df['date'].max()
        if period == 'week':
            start_date = end_date - timedelta(days=6)
        else:  # month
            start_date = end_date - timedelta(days=29)
            
        filtered_df = df[df['date'] >= start_date].copy()
        
        # Extract nested values using loc
        filtered_df.loc[:, 'mood_score'] = filtered_df.apply(lambda x: x['mood']['score'], axis=1)
        filtered_df.loc[:, 'sleep_quality'] = filtered_df.apply(lambda x: x['sleep']['quality'], axis=1)
        
        # Convert date to string format for JSON serialization
        filtered_df['date'] = filtered_df['date'].dt.strftime('%Y-%m-%d')
        
        return filtered_df

    @staticmethod
    def get_recent_records(days: int = 7) -> List[Dict[str, Any]]:
        """Get recent health records"""
        if not st.session_state.health_records:
            return []
        
        # Get the most recent records
        records = st.session_state.health_records[-days:]
        
        # Ensure dates are in string format
        for record in records:
            if isinstance(record.get('date'), datetime):
                record['date'] = record['date'].strftime('%Y-%m-%d')
        
        return records

    @staticmethod
    def add_health_record(record: Dict[str, Any]):
        """Add a new health record"""
        if 'health_records' not in st.session_state:
            st.session_state.health_records = []
        
        # Ensure the date is in string format
        if isinstance(record.get('date'), datetime):
            record['date'] = record['date'].strftime('%Y-%m-%d')
        
        st.session_state.health_records.append(record)
        
        # Keep only last 30 days of data
        if len(st.session_state.health_records) > 30:
            st.session_state.health_records = st.session_state.health_records[-30:]

    @staticmethod
    def generate_realistic_data(start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Generate realistic looking historical data"""
        data = []
        current_date = start_date
        
        # Base patterns for realistic data generation
        base_mood = 7
        base_sleep = 7
        symptom_base = {
            "hot_flashes": 5,
            "night_sweats": 4,
            "headaches": 3,
            "joint_pain": 4
        }
    
    @staticmethod
    def generate_realistic_data(start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Generate realistic looking historical data"""
        data = []
        current_date = start_date
        
        # Base patterns for realistic data generation
        base_mood = 7
        base_sleep = 7
        symptom_base = {
            "hot_flashes": 5,
            "night_sweats": 4,
            "headaches": 3,
            "joint_pain": 4
        }
        
        mood_triggers = [
            "Work Stress", "Family Matters", "Physical Discomfort", 
            "Sleep Quality", "Social Interactions", "Weather", "Exercise"
        ]
        
        sleep_issues = [
            "Difficulty Falling Asleep", "Waking Up During Night",
            "Early Morning Awakening", "Night Sweats", "Disturbing Dreams", "None"
        ]
        
        food_categories = [
            "High Protein", "High Fiber", "High Sugar", "High Fat",
            "Balanced", "Vegetables", "Fruits", "Dairy", "Grains"
        ]
        
        while current_date <= end_date:
            # Add some weekly patterns and random variations
            day_of_week = current_date.weekday()
            weekly_mood_adj = -0.5 if day_of_week in [0, 4] else 0.5  # Lower mood on Monday/Friday
            weekly_sleep_adj = -1 if day_of_week in [5, 6] else 0  # Worse sleep on weekends
            
            # Random variations
            mood_score = min(10, max(1, base_mood + weekly_mood_adj + np.random.normal(0, 1)))
            sleep_quality = min(10, max(1, base_sleep + weekly_sleep_adj + np.random.normal(0, 1)))
            
            # Generate daily record
            daily_record = {
                "date": current_date.strftime("%Y-%m-%d"),
                "mood": {
                    "score": round(mood_score, 1),
                    "triggers": np.random.choice(mood_triggers, size=np.random.randint(1, 3), replace=False).tolist(),
                    "notes": ""
                },
                "sleep": {
                    "bedtime": "22:00",
                    "waketime": "07:00",
                    "quality": round(sleep_quality, 1),
                    "issues": np.random.choice(sleep_issues, size=np.random.randint(1, 3), replace=False).tolist(),
                    "wake_frequency": np.random.randint(0, 4)
                },
                "diet": {
                    "meals": {
                        "breakfast": {
                            "categories": np.random.choice(food_categories, size=np.random.randint(2, 4), replace=False).tolist(),
                            "notes": ""
                        },
                        "lunch": {
                            "categories": np.random.choice(food_categories, size=np.random.randint(2, 4), replace=False).tolist(),
                            "notes": ""
                        },
                        "dinner": {
                            "categories": np.random.choice(food_categories, size=np.random.randint(2, 4), replace=False).tolist(),
                            "notes": ""
                        },
                        "snacks": {
                            "categories": np.random.choice(food_categories, size=np.random.randint(0, 2), replace=False).tolist(),
                            "notes": ""
                        }
                    },
                    "water_intake": np.random.randint(4, 9),
                    "caffeine_intake": np.random.randint(1, 4),
                    "supplements": ["Calcium", "Vitamin D"] if np.random.random() > 0.3 else ["Vitamin D"]
                },
                "symptoms": {
                    "physical": {
                        "hot_flashes": round(min(10, max(1, symptom_base["hot_flashes"] + np.random.normal(0, 1))), 1),
                        "night_sweats": round(min(10, max(1, symptom_base["night_sweats"] + np.random.normal(0, 1))), 1),
                        "headaches": round(min(10, max(1, symptom_base["headaches"] + np.random.normal(0, 1))), 1),
                        "joint_pain": round(min(10, max(1, symptom_base["joint_pain"] + np.random.normal(0, 1))), 1)
                    },
                    "emotional": {
                        "anxiety": round(min(10, max(1, 5 + np.random.normal(0, 1))), 1),
                        "irritability": round(min(10, max(1, 4 + np.random.normal(0, 1))), 1),
                        "mood_swings": round(min(10, max(1, 4 + np.random.normal(0, 1))), 1),
                        "energy_level": round(min(10, max(1, 6 + np.random.normal(0, 1))), 1)
                    },
                    "notes": ""
                }
            }
            
            data.append(daily_record)
            current_date += timedelta(days=1)
        
        return data

    @staticmethod
    def initialize_session_state():
        """Initialize all necessary session state variables"""
        if 'user_data' not in st.session_state:
            st.session_state.user_data = {
                "name": "Jane Doe",
                "age": 52,
                "menopause_stage": "Mid Stage",
                "last_update": datetime.now().strftime("%Y-%m-%d")
            }
        
        if 'health_records' not in st.session_state:
            # Generate 30 days of historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            st.session_state.health_records = DataStore.generate_realistic_data(start_date, end_date)
    
    @staticmethod
    def get_data_for_period(period: str = 'week') -> pd.DataFrame:
        """Get data for specified time period"""
        if not st.session_state.health_records:
            return pd.DataFrame()
        
        # Create a new DataFrame instead of using a view
        df = pd.DataFrame(st.session_state.health_records).copy()
        df['date'] = pd.to_datetime(df['date'])
        
        end_date = df['date'].max()
        if period == 'week':
            start_date = end_date - timedelta(days=6)
        else:  # month
            start_date = end_date - timedelta(days=29)
                
        filtered_df = df[df['date'] >= start_date].copy()
        
        # Extract nested values using loc
        filtered_df.loc[:, 'mood_score'] = filtered_df.apply(lambda x: x['mood']['score'], axis=1)
        filtered_df.loc[:, 'sleep_quality'] = filtered_df.apply(lambda x: x['sleep']['quality'], axis=1)
        
        # Convert date to string format for JSON serialization
        filtered_df['date'] = filtered_df['date'].dt.strftime('%Y-%m-%d')
        
        return filtered_df
    
    @staticmethod
    def add_health_record(record: Dict[str, Any]):
        """Add a new health record"""
        st.session_state.health_records.append(record)
        # Keep only last 30 days of data
        if len(st.session_state.health_records) > 30:
            st.session_state.health_records = st.session_state.health_records[-30:]

# Create singleton instance
data_store = DataStore()