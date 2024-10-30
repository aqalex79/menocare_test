from typing import Dict, Any, Optional
from datetime import datetime
import logging
from pathlib import Path
from .data_manager import DataManager
from .cloud_storage import CloudStorage
from .data_validator import DataPreprocessor, HealthDataValidator

class SyncManager:
    """Manages synchronization between local and cloud storage"""
    
    def __init__(self):
        """Initialize sync manager"""
        self.data_manager = DataManager()
        self.cloud_storage = CloudStorage()
        self.validator = HealthDataValidator()
        self.preprocessor = DataPreprocessor()
        
        # Set up logging
        logging.basicConfig(
            filename='sync_operations.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    async def sync_health_record(self, record: Dict[str, Any]) -> bool:
        """Synchronize new health record"""
        try:
            # Preprocess and validate data
            processed_record = self.preprocessor.process_health_record(record)
            
            # Validate all components
            validations = [
                self.validator.validate_mood_data(processed_record['mood']),
                self.validator.validate_sleep_data(processed_record['sleep']),
                self.validator.validate_diet_data(processed_record['diet']),
                self.validator.validate_symptoms_data(processed_record['symptoms']),
                self.validator.validate_exercise_data(processed_record['exercise'])
            ]
            
            if not all(validations):
                logging.error("Data validation failed")
                return False
            
            # Save to local storage
            self.data_manager.save_daily_record(processed_record)
            
            # Save to cloud storage
            await self.cloud_storage.save_health_record(processed_record)
            
            # Generate and sync feedback
            await self.sync_feedback(processed_record['date'])
            
            logging.info(f"Successfully synced health record for {processed_record['date']}")
            return True
            
        except Exception as e:
            logging.error(f"Error syncing health record: {str(e)}")
            return False
    
    async def sync_feedback(self, date: str) -> bool:
        """Synchronize feedback data"""
        try:
            # Get latest feedback from local storage
            feedback = self.data_manager.get_latest_feedback()
            
            # Save to cloud storage
            await self.cloud_storage.save_feedback(feedback)
            
            logging.info(f"Successfully synced feedback for {date}")
            return True
            
        except Exception as e:
            logging.error(f"Error syncing feedback: {str(e)}")
            return False
    
    async def sync_user_data(self, user_data: Dict[str, Any]) -> bool:
        """Synchronize user data"""
        try:
            # Update local storage
            self.data_manager.update_user_profile(user_data)
            
            # Update cloud storage
            await self.cloud_storage.update_user_data(user_data)
            
            logging.info("Successfully synced user data")
            return True
            
        except Exception as e:
            logging.error(f"Error syncing user data: {str(e)}")
            return False
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get synchronized dashboard data"""
        try:
            # Get local data
            local_data = self.data_manager.get_dashboard_data()
            
            # Get cloud data
            cloud_records = await self.cloud_storage.get_health_records()
            cloud_feedback = await self.cloud_storage.get_feedback_history()
            
            # Merge and return the most recent data
            return {
                "user": local_data["user"],
                "recent_records": self._merge_records(local_data["recent_records"], cloud_records),
                "latest_feedback": self._get_latest_feedback(local_data["latest_feedback"], cloud_feedback),
                "health_score": local_data["health_score"]
            }
            
        except Exception as e:
            logging.error(f"Error getting dashboard data: {str(e)}")
            return {}
    
    def _merge_records(self, local_records: list, cloud_records: list) -> list:
        """Merge local and cloud records, removing duplicates"""
        all_records = local_records + cloud_records
        unique_records = {record["date"]: record for record in all_records}
        return list(unique_records.values())
    
    def _get_latest_feedback(self, local_feedback: dict, cloud_feedback: list) -> dict:
        """Get the most recent feedback from either source"""
        if not cloud_feedback:
            return local_feedback
        if not local_feedback:
            return cloud_feedback[-1] if cloud_feedback else {}
        
        cloud_latest = cloud_feedback[-1]
        return max(
            [local_feedback, cloud_latest],
            key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d")
        )
