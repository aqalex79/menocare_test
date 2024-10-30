import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Dict, Any, List
import json
from datetime import datetime

# Load environment variables at startup
load_dotenv()

class GeminiAPI:
    def __init__(self):
        """Initialize Gemini API with API key"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
    async def analyze_dashboard_data(self, data: Dict[str, Any], period: str = 'week') -> Dict[str, Any]:
        """Analyze dashboard data and provide insights based on time period"""
        try:
            current_data = data.get('current_data', {})
            historical_data = data.get('historical_data', [])
            metrics = data.get('metrics', {})

            prompt = f"""
            As a menopause health expert, analyze this user's health data for the past {period} and provide insights in JSON format:

            Current Data:
            {json.dumps(current_data, indent=2)}

            Historical Data (last {period}):
            {json.dumps(historical_data[-7:], indent=2)}

            Period Metrics:
            {json.dumps(metrics, indent=2)}

            Please provide a comprehensive analysis in the EXACT following JSON format:
            {{
                "overall_assessment": {{
                    "health_score": "Numerical score out of 100 based on all metrics",
                    "period_summary": "Comprehensive summary of health trends and status",
                    "trend": "Change trend with explanation (+/- points)",
                    "score_explanation": "How the health score was calculated"
                }},
                "component_insights": {{
                    "mood": {{
                        "status": "Current mood status and pattern description",
                        "level": "positive/moderate/needs_attention",
                        "quick_review": "Analysis of mood patterns and influencing factors",
                        "recommendations": [
                            "Mood-specific recommendation 1",
                            "Mood-specific recommendation 2"
                        ]
                    }},
                    "sleep": {{
                        "status": "Current sleep status and pattern description",
                        "level": "positive/moderate/needs_attention",
                        "quick_review": "Analysis of sleep patterns and quality factors",
                        "recommendations": [
                            "Sleep-specific recommendation 1",
                            "Sleep-specific recommendation 2"
                        ]
                    }},
                    "symptoms": {{
                        "status": "Current symptoms overview and intensity levels",
                        "level": "positive/moderate/needs_attention",
                        "quick_review": "Analysis of symptom patterns and management",
                        "recommendations": [
                            "Symptom management recommendation 1",
                            "Symptom management recommendation 2"
                        ]
                    }}
                }}
            }}

            Focus on:
            1. Recent trends and changes in each health component
            2. Relationships between different health aspects
            3. Personalized recommendations based on patterns
            4. Clear, actionable insights
            5. Both immediate and long-term improvements
            """

            # Generate analysis
            response = self.model.generate_content(prompt)
            response.resolve()
            print("Raw API Response:", response.text)

            try:
                text = response.text.strip()
                if text.startswith('```json'):
                    text = text.split('```json')[1]
                if text.endswith('```'):
                    text = text.rsplit('```', 1)[0]
                text = text.strip()
                
                return json.loads(text)
                
            except json.JSONDecodeError as je:
                print("JSON Parse Error:", str(je))
                print("Attempted to parse text:", text)
                return self._get_default_dashboard_response(period)
                
        except Exception as e:
            print(f"API Error: {str(e)}")
            return self._get_default_dashboard_response(period)

    def _get_default_dashboard_response(self, period: str) -> Dict[str, Any]:
        """Get default dashboard analysis response"""
        return {
            "overall_assessment": {
                "health_score": "N/A",
                "period_summary": f"Unable to analyze health data for the {period}",
                "trend": "Unable to calculate trend",
                "score_explanation": "Health score calculation unavailable"
            },
            "component_insights": {
                "mood": {
                    "status": "Analysis unavailable",
                    "level": "moderate",
                    "quick_review": "Unable to analyze mood patterns",
                    "recommendations": [
                        "Continue monitoring your mood",
                        "Maintain regular check-ins"
                    ]
                },
                "sleep": {
                    "status": "Analysis unavailable",
                    "level": "moderate",
                    "quick_review": "Unable to analyze sleep patterns",
                    "recommendations": [
                        "Maintain regular sleep schedule",
                        "Track sleep quality daily"
                    ]
                },
                "symptoms": {
                    "status": "Analysis unavailable",
                    "level": "moderate",
                    "quick_review": "Unable to analyze symptom patterns",
                    "recommendations": [
                        "Continue monitoring symptoms",
                        "Note any significant changes"
                    ]
                }
            }
        }

    async def analyze_daily_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze specific module data with enhanced context"""
        try:
            module_type = data.get('module_type', '').lower()
            current_data = data.get('current_data', {})
            historical_data = data.get('historical_data', [])[-7:]  # Last 7 records
            
            # Module-specific analysis prompts
            module_prompts = {
                'mood': """
                    Key focus areas for mood analysis:
                    - Mood score trends and patterns
                    - Impact of identified triggers
                    - Emotional well-being indicators
                    - Correlation with other health factors
                """,
                'sleep': """
                    Key focus areas for sleep analysis:
                    - Sleep quality patterns
                    - Sleep duration and consistency
                    - Sleep disruption factors
                    - Impact on daily well-being
                """,
                'symptoms': """
                    Key focus areas for symptoms analysis:
                    - Symptom intensity patterns
                    - Physical vs emotional symptom relationships
                    - Trigger identification
                    - Management effectiveness
                """,
                'diet': """
                    Key focus areas for diet analysis:
                    - Nutritional balance
                    - Meal timing and patterns
                    - Hydration levels
                    - Supplement effectiveness
                """
            }
            
            # Build module-specific prompt
            base_prompt = f"""
            As a menopause health expert, analyze this user's {module_type} data and provide detailed insights:

            Today's {module_type} Data:
            {json.dumps(current_data, indent=2)}

            Recent History (Last 7 days):
            {json.dumps(historical_data, indent=2)}

            {module_prompts.get(module_type, '')}

            Provide a comprehensive analysis in the following JSON format:
            {{
                "today_insights": [
                    "Detailed analysis point about today's data",
                    "Pattern recognition from recent history",
                    "Notable changes or concerns",
                    "Positive developments or improvements"
                ],
                "recommendations": [
                    "Specific, actionable recommendation based on current data",
                    "Lifestyle adjustment suggestion",
                    "Preventive measure or management strategy",
                    "Long-term improvement suggestion"
                ]
            }}

            Analysis requirements:
            1. Provide specific, data-driven insights
            2. Include both short-term and long-term patterns
            3. Focus on actionable recommendations
            4. Consider menopause stage context
            5. Note any concerning trends that need attention
            """

            # Generate analysis
            response = self.model.generate_content(base_prompt)
            response.resolve()
            
            # Clean and parse response
            text = response.text.strip()
            if text.startswith('```json'):
                text = text.split('```json')[1]
            if text.endswith('```'):
                text = text.rsplit('```', 1)[0]
            text = text.strip()
            
            try:
                analysis = json.loads(text)
                # Ensure minimum required structure
                if not isinstance(analysis.get('today_insights'), list):
                    analysis['today_insights'] = []
                if not isinstance(analysis.get('recommendations'), list):
                    analysis['recommendations'] = []
                return analysis
            
            except json.JSONDecodeError:
                return self._get_default_module_response(module_type)
            
        except Exception as e:
            print(f"API Error ({module_type}): {str(e)}")
            return self._get_default_module_response(module_type)

    def _get_default_module_response(self, module_type: str) -> Dict[str, Any]:
        """Get default response for specific module type"""
        default_responses = {
            'mood': {
                "today_insights": [
                    "Continue monitoring your mood patterns",
                    "Track any significant mood changes",
                ],
                "recommendations": [
                    "Maintain regular mood tracking",
                    "Practice stress management techniques",
                    "Seek support when needed"
                ]
            },
            'sleep': {
                "today_insights": [
                    "Keep monitoring your sleep patterns",
                    "Note any sleep disruptions",
                ],
                "recommendations": [
                    "Maintain consistent sleep schedule",
                    "Create a relaxing bedtime routine",
                    "Monitor sleep environment"
                ]
            },
            'symptoms': {
                "today_insights": [
                    "Continue tracking symptom intensity",
                    "Monitor symptom patterns",
                ],
                "recommendations": [
                    "Record any new symptoms",
                    "Track symptom triggers",
                    "Discuss persistent symptoms with healthcare provider"
                ]
            },
            'diet': {
                "today_insights": [
                    "Monitor your eating patterns",
                    "Track nutritional intake",
                ],
                "recommendations": [
                    "Maintain balanced nutrition",
                    "Stay hydrated throughout the day",
                    "Consider regular meal timing"
                ]
            }
        }
        
        return default_responses.get(module_type, {
            "today_insights": [
                "Continue monitoring your health metrics",
                "Track any significant changes"
            ],
            "recommendations": [
                "Maintain regular health tracking",
                "Follow your usual health routines",
                "Consult healthcare provider if needed"
            ]
        })

# Create singleton instance
gemini_api = GeminiAPI()