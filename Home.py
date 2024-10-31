import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.data_store import data_store
from utils.gemini_api import gemini_api
import asyncio

# Page configuration
st.set_page_config(
    page_title="MenoCare - Health Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data store
data_store.initialize_session_state()

def render_user_info():
    """Display user information in sidebar"""
    try:
        user = st.session_state.user_data
        st.sidebar.image("https://api.dicebear.com/7.x/big-ears/svg?seed=Jane&mood=happy", width=150)
        st.sidebar.title(f"👋 Welcome, {user['name']}")
        st.sidebar.markdown(f"""
        #### Personal Information
        - 🎂 Age: {user['age']} years
        - 📅 Menopause Stage: {user['menopause_stage']}
        - 🕒 Last Updated: {user['last_update']}
        """)
        
        # Add time period selector to sidebar
        period = st.sidebar.radio(
            "Select Time Period",
            options=["week", "month"],
            format_func=lambda x: "Past Week" if x == "week" else "Past Month",
            key="time_period"
        )
        
        return period
        
    except Exception as e:
        st.sidebar.error("Error loading user profile")
        return "week"  # default to week view

async def render_overall_assessment(period: str):
    """Render overall health assessment with AI insights"""
    try:
        # Get data for selected period
        df = data_store.get_data_for_period(period)
        if df.empty:
            st.warning("No data available for the selected period")
            return

        recent_records = df.to_dict('records')
        latest = recent_records[-1]
        
        # Calculate base metrics
        metrics = {
            "avg_mood": float(df['mood_score'].mean()),
            "avg_sleep": float(df['sleep_quality'].mean()),
            "mood_trend": float(df['mood_score'].iloc[-1] - df['mood_score'].iloc[0]),
            "sleep_trend": float(df['sleep_quality'].iloc[-1] - df['sleep_quality'].iloc[0]),
            "period_length": len(df)
        }
        
        # Prepare data for AI analysis
        analysis_data = {
            "current_data": latest,
            "historical_data": recent_records,
            "metrics": metrics,
            "period": period
        }
        
        # Get AI insights
        insights = await gemini_api.analyze_dashboard_data(analysis_data, period)
        
        if insights and insights.get("overall_assessment"):
            # Overall Score Section
            st.header("🎯 Overall Health Assessment")
            
            # Create two columns for score and summary
            score_col, summary_col = st.columns([1, 2])
            
            with score_col:
                if insights["overall_assessment"].get("health_score") != "N/A":
                    score_value = insights["overall_assessment"]["health_score"]
                    trend = insights["overall_assessment"].get("trend", "")
                    st.metric(
                        "Health Score",
                        value=score_value,
                        delta=trend if trend else None
                    )
                else:
                    st.metric("Health Score", "N/A")
            
            with summary_col:
                st.subheader("Summary")
                if insights["overall_assessment"].get("period_summary"):
                    st.write(insights["overall_assessment"]["period_summary"])
                else:
                    st.write("Unable to generate summary for the selected period")
        else:
            st.error("Unable to generate health assessment. Please try again.")
            
    except Exception as e:
        st.error("Error loading health assessment")
        with st.expander("Debug Info"):
            st.write(f"Error: {str(e)}")

async def render_component_section(df: pd.DataFrame, component_data: dict, insights: dict, title: str, component_key: str):
    """Render a health component section with analysis"""
    try:
        st.subheader(title)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if component_key in ["mood", "sleep"]:
                # Line chart for mood or sleep
                score_key = 'mood_score' if component_key == 'mood' else 'sleep_quality'
                fig = px.line(df, x='date', y=score_key,
                            title=f"Your {title} Trend",
                            labels={score_key: f'{title} Score', 'date': 'Date'})
                fig.update_traces(line=dict(width=3))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Bar chart for symptoms
                if "physical" in component_data:
                    symptoms = component_data["physical"]
                    fig = px.bar(
                        x=list(symptoms.keys()),
                        y=list(symptoms.values()),
                        title="Current Symptom Levels",
                        labels={'x': 'Symptoms', 'y': 'Intensity'}
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            component_insights = insights.get("component_insights", {}).get(component_key, {})
            
            # Current Status
            if component_key == "mood":
                current_score = component_data.get("score", "N/A")
                st.metric(f"Current {title}", 
                         f"{current_score}/10" if current_score != "N/A" else "N/A")
            elif component_key == "sleep":
                current_score = component_data.get("quality", "N/A")
                st.metric(f"Current {title}", 
                         f"{current_score}/10" if current_score != "N/A" else "N/A")
            elif "physical" in component_data:
                max_symptom = max(component_data["physical"].values(), default="N/A")
                st.metric("Symptom Intensity", 
                         f"{max_symptom}/10" if max_symptom != "N/A" else "N/A")
            
            # Analysis Sections
            if component_insights:
                with st.container():
                    st.markdown("##### Quick Review")
                    st.write(component_insights.get("quick_review", "Analysis not available"))
                    
                    st.markdown("##### Recommendations")
                    recommendations = component_insights.get("recommendations", [])
                    if recommendations:
                        for rec in recommendations:
                            st.info(f"💡 {rec}")
                    else:
                        st.info("💡 Continue monitoring and tracking your health data")
            else:
                st.warning("Analysis not available for this component")
                
    except Exception as e:
        st.error(f"Error rendering {title} section")
        with st.expander("Debug Info"):
            st.write(f"Error: {str(e)}")

async def render_detailed_sections(period: str):
    """Render detailed health sections with AI insights"""
    try:
        # Get data for the selected period
        df = data_store.get_data_for_period(period)
        recent_records = df.to_dict('records')
        latest = recent_records[-1] if recent_records else None
        
        if not latest:
            st.warning("No data available for selected period")
            return
        
        # Get AI analysis
        analysis_data = {
            "current_data": latest,
            "historical_data": recent_records,
            "metrics": {
                "avg_mood": df['mood_score'].mean(),
                "avg_sleep": df['sleep_quality'].mean(),
                "trend_direction": "improving" if df['mood_score'].iloc[-1] > df['mood_score'].iloc[0] else "declining"
            }
        }
        
        insights = await gemini_api.analyze_dashboard_data(analysis_data, period)
        
        if insights:
            st.header("📊 Detailed Health Components")
            
            # Render each component section
            await render_component_section(
                df, latest["mood"], insights, "😊 Mood", "mood"
            )
            st.divider()
            
            await render_component_section(
                df, latest["sleep"], insights, "😴 Sleep", "sleep"
            )
            st.divider()
            
            await render_component_section(
                df, latest["symptoms"], insights, "🌡️ Symptoms", "symptoms"
            )
            
    except Exception as e:
        st.error("Error loading health details")
        with st.expander("Debug Info"):
            st.write(e)

async def main():
    # Get selected time period from sidebar
    period = render_user_info()
    
    st.title("Your Health Dashboard")
    st.markdown(f"""
    Here's your health overview for the past {period}. Track your progress and get 
    personalized insights to help manage your wellness journey.
    """)
    
    # Overall assessment
    await render_overall_assessment(period)
    st.divider()
    
    # Detailed sections
    await render_detailed_sections(period)

if __name__ == "__main__":
    asyncio.run(main())