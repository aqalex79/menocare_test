from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class ResponseHandler:
    """Handles and processes Gemini API responses"""
    
    @staticmethod
    def process_daily_analysis(response: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate daily analysis response"""
        try:
            required_keys = ["insights", "concerns", "recommendations", "lifestyle_adjustments"]
            
            # Ensure all required keys exist
            for key in required_keys:
                if key not in response:
                    response[key] = []
            
            # Ensure all values are lists
            for key in required_keys:
                if not isinstance(response[key], list):
                    response[key] = [response[key]] if response[key] else []
            
            return {
                "timestamp": datetime.now().isoformat(),
                "analysis": response
            }
            
        except Exception as e:
            print(f"Error processing daily analysis: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "analysis": {
                    "insights": ["Error processing analysis"],
                    "concerns": [],
                    "recommendations": [],
                    "lifestyle_adjustments": []
                }
            }
    
    @staticmethod
    def process_health_education(response: str) -> Dict[str, Any]:
        """Process health education response"""
        try:
            # Split content into sections
            sections = response.split('\n\n')
            
            return {
                "timestamp": datetime.now().isoformat(),
                "content": response,
                "sections": sections,
                "summary": sections[0] if sections else ""
            }
            
        except Exception as e:
            print(f"Error processing health education: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "content": "Error generating content",
                "sections": [],
                "summary": "Please try again later"
            }
    
    @staticmethod
    def process_feedback(response: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate feedback response"""
        try:
            # Ensure required structure exists
            if "analysis" not in response:
                response["analysis"] = {}
            if "recommendations" not in response:
                response["recommendations"] = {}
            if "action_plan" not in response:
                response["action_plan"] = []
            
            return {
                "timestamp": datetime.now().isoformat(),
                "feedback": response
            }
            
        except Exception as e:
            print(f"Error processing feedback: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "feedback": {
                    "analysis": {},
                    "recommendations": {},
                    "action_plan": []
                }
            }

    @staticmethod
    def validate_response(response: Dict[str, Any]) -> bool:
        """Validate response structure and content"""
        try:
            # Check if response is properly formatted
            if not isinstance(response, dict):
                return False
            
            # Check if timestamp exists and is valid
            if "timestamp" not in response:
                return False
                
            return True
            
        except Exception:
            return False
