from .gemini_api import GeminiAPI
from .response_handler import ResponseHandler
from typing import Dict, Any, List, Optional
import os

class AIManager:
    """Manages AI integrations and responses for MenoCare"""
    
    def __init__(self):
        """Initialize AI Manager with necessary components"""
        api_key = os.getenv("GOOGLE_API_KEY")
        self.gemini = GeminiAPI(api_key)
        self.handler = ResponseHandler()
    
    async def process_daily_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process daily health input and generate analysis"""
        try:
            # Get analysis from Gemini
            analysis = await self.gemini.analyze_daily_input(data)
            
            # Process and validate response
            processed_response = self.handler.process_daily_analysis(analysis)
            
            if self.handler.validate_response(processed_response):
                return processed_response
            raise ValueError("Invalid response format")
            
        except Exception as e:
            print(f"Error in daily input processing: {str(e)}")
            return {
                "error": "Unable to process daily input",
                "message": str(e)
            }
    
    async def get_health_education(self, 
                                 topic: str,
                                 user_profile: Dict[str, Any],
                                 health_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Get personalized health education content"""
        try:
            # Get content from Gemini
            content = await self.gemini.generate_health_education(
                topic, user_profile, health_patterns
            )
            
            # Process and validate response
            processed_response = self.handler.process_health_education(content)
            
            if self.handler.validate_response(processed_response):
                return processed_response
            raise ValueError("Invalid response format")
            
        except Exception as e:
            print(f"Error in health education generation: {str(e)}")
            return {
                "error": "Unable to generate health education content",
                "message": str(e)
            }
    
    async def generate_personalized_feedback(self,
                                           records: List[Dict[str, Any]],
                                           current_data: Dict[str, Any],
                                           user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized feedback based on health data"""
        try:
            # Get feedback from Gemini
            feedback = await self.gemini.generate_feedback(
                records, current_data, user_profile
            )
            
            # Process and validate response
            processed_response = self.handler.process_feedback(feedback)
            
            if self.handler.validate_response(processed_response):
                return processed_response
            raise ValueError("Invalid response format")
            
        except Exception as e:
            print(f"Error in feedback generation: {str(e)}")
            return {
                "error": "Unable to generate feedback",
                "message": str(e)
            }

# Create singleton instance
ai_manager = AIManager()
