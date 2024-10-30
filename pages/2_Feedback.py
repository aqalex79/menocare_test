import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np
from utils.data_store import data_store
from utils.gemini_api import gemini_api
import asyncio

# Page configuration
st.set_page_config(
    page_title="MenoCare - Health Analysis & Progress",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data store
data_store.initialize_session_state()

def render_user_info():
    """Display user information in sidebar"""
    user = st.session_state.user_data
    st.sidebar.image("https://api.dicebear.com/7.x/micah/svg?seed=Jane", width=150)
    st.sidebar.title(f"👋 Welcome, {user['name']}")
    st.sidebar.markdown(f"""
    #### Personal Information
    - 🎂 Age: {user['age']} years
    - 📅 Menopause Stage: {user['menopause_stage']}
    - 🕒 Last Updated: {user['last_update']}
    """)

def show_basic_trends(recent_records):
    """Display simplified trend visualizations"""
    st.header("📊 Weekly Overview")
    
    # Basic metrics
    col1, col2, col3 = st.columns(3)
    
    # Mood trend
    mood_scores = [record['mood']['score'] for record in recent_records]
    avg_mood = np.mean(mood_scores)
    mood_trend = mood_scores[-1] - mood_scores[0] if len(mood_scores) > 1 else 0
    with col1:
        st.metric("Average Mood", f"{avg_mood:.1f}/10", f"{mood_trend:+.1f}")
    
    # Sleep trend
    sleep_quality = [record['sleep']['quality'] for record in recent_records]
    avg_sleep = np.mean(sleep_quality)
    sleep_trend = sleep_quality[-1] - sleep_quality[0] if len(sleep_quality) > 1 else 0
    with col2:
        st.metric("Sleep Quality", f"{avg_sleep:.1f}/10", f"{sleep_trend:+.1f}")
    
    # Symptom intensity
    physical_symptoms = []
    for record in recent_records:
        avg_symptoms = np.mean(list(record['symptoms']['physical'].values()))
        physical_symptoms.append(avg_symptoms)
    avg_symptoms = np.mean(physical_symptoms)
    symptom_trend = physical_symptoms[-1] - physical_symptoms[0] if len(physical_symptoms) > 1 else 0
    with col3:
        st.metric("Symptom Intensity", f"{avg_symptoms:.1f}/10", f"{symptom_trend:+.1f}")

def show_historical_analysis(analysis):
    """Display comprehensive historical analysis results"""
    try:
        # Weekly Summary
        if analysis.get("weekly_summary"):
            st.header("📋 Weekly Health Summary")
            st.subheader("Overall Wellbeing")
            st.write(analysis["weekly_summary"].get("overall_wellbeing", "Analysis not available"))
            
            st.subheader("Key Observations")
            for observation in analysis["weekly_summary"].get("key_observations", []):
                st.info(observation)
        
        # Detailed Analysis
        if analysis.get("detailed_analysis"):
            st.header("🔍 Detailed Pattern Analysis")
            
            detailed = analysis["detailed_analysis"]
            
            # Mood Patterns
            if "mood_patterns" in detailed:
                st.subheader("😊 Mood Patterns")
                mood = detailed["mood_patterns"]
                st.write("**Trend:**", mood.get("trend", "Not available"))
                st.write("**Common Triggers:**")
                for trigger in mood.get("triggers", []):
                    st.write(f"• {trigger}")
                st.write("**Improvements:**", mood.get("improvements", "Not available"))
                st.write("**Challenges:**", mood.get("challenges", "Not available"))
            
            # Sleep Patterns
            if "sleep_patterns" in detailed:
                st.subheader("😴 Sleep Patterns")
                sleep = detailed["sleep_patterns"]
                st.write("**Trend:**", sleep.get("trend", "Not available"))
                st.write("**Common Issues:**")
                for issue in sleep.get("common_issues", []):
                    st.write(f"• {issue}")
                st.write("**Improvements:**", sleep.get("improvements", "Not available"))
                st.write("**Challenges:**", sleep.get("challenges", "Not available"))
            
            # Symptom Patterns
            if "symptom_patterns" in detailed:
                st.subheader("🌡️ Symptom Patterns")
                
                symptoms = detailed["symptom_patterns"]
                
                # Physical Symptoms
                if "physical" in symptoms:
                    physical = symptoms["physical"]
                    st.write("**Physical Symptoms Trend:**", physical.get("trend", "Not available"))
                    st.write("**Most Significant Physical Symptoms:**")
                    for symptom in physical.get("most_significant", []):
                        st.write(f"• {symptom}")
                    if physical.get("improvements"):
                        st.write("**Improvements:**", physical["improvements"])
                    if physical.get("challenges"):
                        st.write("**Challenges:**", physical["challenges"])
                
                # Emotional Symptoms
                if "emotional" in symptoms:
                    emotional = symptoms["emotional"]
                    st.write("**Emotional Symptoms Trend:**", emotional.get("trend", "Not available"))
                    st.write("**Most Significant Emotional Symptoms:**")
                    for symptom in emotional.get("most_significant", []):
                        st.write(f"• {symptom}")
                    if emotional.get("improvements"):
                        st.write("**Improvements:**", emotional["improvements"])
                    if emotional.get("challenges"):
                        st.write("**Challenges:**", emotional["challenges"])
        
        # Lifestyle Impact
        if analysis.get("lifestyle_impact"):
            st.header("💫 Lifestyle Impact Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("✅ Positive Factors")
                for factor in analysis["lifestyle_impact"].get("positive_factors", []):
                    st.success(f"• {factor}")
                    
            with col2:
                st.subheader("⚠️ Areas Needing Attention")
                for area in analysis["lifestyle_impact"].get("areas_for_attention", []):
                    st.warning(f"• {area}")
        
        # Strategic Recommendations
        if analysis.get("strategic_recommendations"):
            st.header("💡 Strategic Planning")
            recs = analysis["strategic_recommendations"]
            
            if recs.get("immediate_focus"):
                st.subheader("🎯 Immediate Focus Areas")
                for focus in recs["immediate_focus"]:
                    st.info(f"• {focus}")
            
            if recs.get("long_term_strategies"):
                st.subheader("📈 Long-term Strategies")
                for strategy in recs["long_term_strategies"]:
                    st.success(f"• {strategy}")
            
            if recs.get("lifestyle_adjustments"):
                st.subheader("🔄 Lifestyle Adjustments")
                for adjustment in recs["lifestyle_adjustments"]:
                    st.write(f"• {adjustment}")
    
    except Exception as e:
        st.error(f"Error displaying analysis: {str(e)}")
        with st.expander("Debug Info"):
            st.write("Analysis data structure:")
            st.write(analysis)
            st.write("Error details:")
            st.write(e)

async def main():
    render_user_info()
    
    st.title("Weekly Health Analysis & Progress Report")
    st.markdown("""
    This report provides a comprehensive analysis of your health patterns over the past week,
    highlighting trends, improvements, and areas needing attention.
    """)
    
    # Get recent records for analysis
    recent_records = data_store.get_recent_records()
    
    # Get AI analysis of historical patterns
    with st.spinner('Analyzing your weekly health patterns...'):
        try:
            historical_data = data_store.get_recent_records()
            current_data = historical_data[-1] if historical_data else None
            
            if current_data:
                # Show basic metrics
                show_basic_trends(recent_records)
                st.divider()
                
                # Request historical pattern analysis
                analysis_prompt = {
                    "current_data": current_data,
                    "historical_data": historical_data,
                    "analysis_type": "historical"
                }
                
                analysis = await gemini_api.analyze_daily_input(analysis_prompt)
                
                if analysis:
                    # Show comprehensive analysis and recommendations
                    show_historical_analysis(analysis)
                else:
                    st.error("Unable to generate analysis. Please try again later.")
            else:
                st.warning("No health data available for analysis.")
                
        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")
            with st.expander("Debug Info"):
                st.write(e)

if __name__ == "__main__":
    asyncio.run(main())