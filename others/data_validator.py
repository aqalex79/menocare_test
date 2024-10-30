from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd

class HealthDataValidator:
    """Validates health data before storage"""
    
    @staticmethod
    def validate_mood_data(data: Dict[str, Any]) -> bool:
        """Validate mood data"""
        required_fields = {'score', 'triggers', 'notes'}
        if not all(field in data for field in required_fields):
            return False
        
        # Validate score range
        if not (1 <= data['score'] <= 10):
            return False
        
        # Validate triggers format
        if not isinstance(data['triggers'], list):
            return False
        
        return True
    
    @staticmethod
    def validate_sleep_data(data: Dict[str, Any]) -> bool:
        """Validate sleep data"""
        required_fields = {'hours', 'quality', 'issues'}
        if not all(field in data for field in required_fields):
            return False
        
        # Validate hours range
        if not (0 <= data['hours'] <= 24):
            return False
        
        # Validate quality range
        if not (1 <= data['quality'] <= 10):
            return False
        
        return True
    
    @staticmethod
    def validate_diet_data(data: Dict[str, Any]) -> bool:
        """Validate diet data"""
        required_fields = {'meals', 'water_intake', 'supplements'}
        if not all(field in data for field in required_fields):
            return False
        
        # Validate water intake range
        if not (0 <= data['water_intake'] <= 30):
            return False
        
        # Validate meals format
        if not isinstance(data['meals'], list):
            return False
        
        return True
    
    @staticmethod
    def validate_symptoms_data(data: Dict[str, Any]) -> bool:
        """Validate symptoms data"""
        required_fields = {'physical', 'emotional', 'intensity'}
        if not all(field in data for field in required_fields):
            return False
        
        # Validate intensity values
        for category in ['physical', 'emotional']:
            if not all(0 <= intensity <= 10 for intensity in data[category].values()):
                return False
        
        return True
    
    @staticmethod
    def validate_exercise_data(data: Dict[str, Any]) -> bool:
        """Validate exercise data"""
        required_fields = {'type', 'duration', 'intensity'}
        if not all(field in data for field in required_fields):
            return False
        
        # Validate duration range (in minutes)
        if not (0 <= data['duration'] <= 300):
            return False
        
        # Validate intensity values
        valid_intensities = {'Low', 'Moderate', 'High'}
        if data['intensity'] not in valid_intensities:
            return False
        
        return True

class DataPreprocessor:
    """Preprocesses health data before analysis"""
    
    @staticmethod
    def normalize_dates(data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize date formats in the data"""
        if 'date' in data:
            data['date'] = pd.to_datetime(data['date']).strftime('%Y-%m-%d')
        return data
    
    @staticmethod
    def standardize_scores(data: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize all scores to 0-10 scale"""
        if 'mood' in data and 'score' in data['mood']:
            data['mood']['score'] = round(float(data['mood']['score']), 1)
        
        if 'sleep' in data and 'quality' in data['sleep']:
            data['sleep']['quality'] = round(float(data['sleep']['quality']), 1)
        
        return data
    
    @staticmethod
    def clean_text_fields(data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and standardize text fields"""
        if 'mood' in data and 'notes' in data['mood']:
            data['mood']['notes'] = data['mood']['notes'].strip()
        
        if 'diet' in data and 'notes' in data['diet']:
            data['diet']['notes'] = data['diet']['notes'].strip()
        
        return data
    
    @staticmethod
    def process_health_record(data: Dict[str, Any]) -> Dict[str, Any]:
        """Process complete health record"""
        data = DataPreprocessor.normalize_dates(data)
        data = DataPreprocessor.standardize_scores(data)
        data = DataPreprocessor.clean_text_fields(data)
        return data
