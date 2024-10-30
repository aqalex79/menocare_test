from .data_manager import DataManager
from .cloud_storage import CloudStorage
from .sync_manager import SyncManager
from .data_validator import HealthDataValidator, DataPreprocessor

class MenoCareData:
    """Main data handling class for MenoCare"""
    
    def __init__(self):
        self.sync_manager = SyncManager()
    
    async def save_daily_input(self, data: dict) -> bool:
        """Save daily health input"""
        return await self.sync_manager.sync_health_record(data)
    
    async def get_dashboard_data(self) -> dict:
        """Get dashboard data"""
        return await self.sync_manager.get_dashboard_data()
    
    async def update_user_profile(self, data: dict) -> bool:
        """Update user profile"""
        return await self.sync_manager.sync_user_data(data)
    
    def get_latest_feedback(self) -> dict:
        """Get latest feedback"""
        return self.sync_manager.data_manager.get_latest_feedback()

# Create a singleton instance
menocare_data = MenoCareData()

__all__ = ['menocare_data']