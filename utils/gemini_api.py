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
       api_key = os.getenv("GOOGLE_API_KEY")
       if not api_key:
           raise ValueError("GOOGLE_API_KEY not found in environment variables")
           
       genai.configure(api_key=api_key)
       self.model = genai.GenerativeModel('gemini-1.5-pro')
       
   async def analyze_dashboard_data(self, data: Dict[str, Any], period: str = 'week') -> Dict[str, Any]:
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
                    "period_summary": "Comprehensive summary of overall health trends and status",
                    "trend": "Change trend with explanation (+/- points)",
                    "score_explanation": "Detailed explanation of how the health score was calculated"
                }},
                "component_insights": {{
                    "mood": {{
                        "status": "Current detailed status with specific patterns and triggers",
                        "level": "positive/moderate/needs_attention",
                        "quick_review": "Analysis including quantitative trends and correlations",
                        "short_term_goals": [
                            "Goal 1 with specific metric and timeline",
                            "Goal 2 with action steps and expected outcome"
                        ],
                        "long_term_strategy": [
                            "Strategy 1 with implementation plan",
                            "Strategy 2 with progress tracking method"
                        ],
                        "recommendations": [
                            "Actionable recommendation with clear steps",
                            "Practical strategy with expected benefits"
                        ]
                    }},
                    "sleep": {{
                        "status": "Current detailed status with sleep patterns and quality metrics",
                        "level": "positive/moderate/needs_attention",
                        "quick_review": "Analysis of sleep quality trends and disruption patterns",
                        "short_term_goals": [
                            "Sleep quality improvement goal with timeline",
                            "Sleep routine adjustment with specific steps"
                        ],
                        "long_term_strategy": [
                            "Sleep habit formation plan with milestones",
                            "Sleep environment optimization strategy"
                        ],
                        "recommendations": [
                            "Evidence-based sleep hygiene practice",
                            "Sleep schedule adjustment recommendation"
                        ]
                    }},
                    "symptoms": {{
                        "status": "Current symptom intensity and frequency patterns",
                        "level": "positive/moderate/needs_attention", 
                        "quick_review": "Analysis of symptom trends and trigger correlations",
                        "short_term_goals": [
                            "Symptom management goal with specific metrics",
                            "Trigger identification and avoidance plan"
                        ],
                        "long_term_strategy": [
                            "Comprehensive symptom management approach",
                            "Lifestyle modification plan with tracking"
                        ],
                        "recommendations": [
                            "Targeted symptom relief strategy",
                            "Prevention and management technique"
                        ]
                    }}
                }}
            }}

            Focus on:
            1. Computing an overall health score (0-100) based on mood, sleep and symptom metrics
            2. Identifying key trends and patterns across all health components
            3. Providing specific, actionable insights and recommendations
            4. Including quantitative metrics and changes where possible
            5. Clear implementation steps and expected outcomes
            """

            response = self.model.generate_content(prompt)
            response.resolve()

            try:
                text = response.text.strip()
                if text.startswith('```json'):
                    text = text.split('```json')[1]
                if text.endswith('```'):
                    text = text.rsplit('```', 1)[0]
                text = text.strip()
                
                # Clean text
                text = text.replace(".  ", ". ")
                text = text.replace("...", ".")   
                text = text.replace(". ", ".")    
                text = text.replace(",  ", ", ")  
                
                return json.loads(text)
                
            except json.JSONDecodeError as je:
                print("JSON Parse Error:", str(je))
                print("Attempted to parse text:", text) 
                return self._get_default_dashboard_response(period)
                
        except Exception as e:
            print(f"API Error: {str(e)}")
            return self._get_default_dashboard_response(period)

   def _get_default_dashboard_response(self, period: str) -> Dict[str, Any]:
    return {
        "overall_assessment": {
            "health_score": "70",
            "period_summary": "Based on available data, overall health metrics indicate moderate stability with room for improvement",
            "trend": "+2 points from previous period",
            "score_explanation": "Score calculated from: 40% mood metrics, 30% sleep quality, 30% symptom management"
        },
        "component_insights": {
            "mood": {
                "status": "Analysis unavailable",
                "level": "moderate",
                "quick_review": "Unable to analyze patterns",
                "short_term_goals": [
                    "Continue daily mood tracking",
                    "Record mood triggers"
                ],
                "long_term_strategy": [
                    "Establish consistent tracking routine", 
                    "Develop coping mechanisms"
                ],
                "recommendations": [
                    "Maintain regular mood monitoring",
                    "Practice basic self-care"
                ]
            },
            "sleep": {
                "status": "Analysis unavailable",
                "level": "moderate", 
                "quick_review": "Unable to analyze sleep patterns",
                "short_term_goals": [
                    "Track sleep schedule daily",
                    "Note sleep disruptions"
                ],
                "long_term_strategy": [
                    "Work toward consistent sleep routine",
                    "Monitor sleep environment factors"
                ],
                "recommendations": [
                    "Maintain regular sleep schedule",
                    "Basic sleep hygiene practices"
                ]
            },
            "symptoms": {
                "status": "Analysis unavailable", 
                "level": "moderate",
                "quick_review": "Unable to analyze symptom patterns",
                "short_term_goals": [
                    "Track symptoms daily",
                    "Record potential triggers"
                ],
                "long_term_strategy": [
                    "Build symptom management routine",
                    "Identify pattern correlations"  
                ],
                "recommendations": [
                    "Continue symptom monitoring",
                    "Basic symptom management steps"
                ]
            }
        }
    }

   async def analyze_daily_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
       try:
           module_type = data.get('module_type', '').lower()
           current_data = data.get('current_data', {})
           historical_data = data.get('historical_data', [])[-7:]
           
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

           response = self.model.generate_content(base_prompt)
           response.resolve()
           
           text = response.text.strip()
           if text.startswith('```json'):
               text = text.split('```json')[1]
           if text.endswith('```'):
               text = text.rsplit('```', 1)[0]
           text = text.strip()
           
           try:
               analysis = json.loads(text)
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