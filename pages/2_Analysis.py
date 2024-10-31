import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

def render_user_info():
    """Display user information and time period selector in sidebar"""
    user = st.session_state.user_data
    st.sidebar.image("https://api.dicebear.com/7.x/big-ears/svg?seed=Jane&mood=happy", width=150)
    st.sidebar.title(f"👋 Welcome, {user['name']}")
    st.sidebar.markdown(f"""
    #### Personal Information
    - 🎂 Age: {user['age']} years
    - 📅 Menopause Stage: {user['menopause_stage']}
    - 🕒 Last Updated: {user['last_update']}
    """)
    
    period = st.sidebar.radio(
        "Select Time Period",
        options=["week", "month"],
        format_func=lambda x: "Past Week" if x == "week" else "Past Month",
        key="analysis_period"
    )
    return period

def calculate_metrics(data):
    """Calculate key metrics from data"""
    metrics = {
        'mood': {
            'avg': np.mean([r['mood']['score'] for r in data]),
            'min': min([r['mood']['score'] for r in data]),
            'max': max([r['mood']['score'] for r in data]),
            'trend': (data[-1]['mood']['score'] - data[0]['mood']['score'])
        },
        'sleep': {
            'avg': np.mean([r['sleep']['quality'] for r in data]),
            'min': min([r['sleep']['quality'] for r in data]),
            'max': max([r['sleep']['quality'] for r in data]),
            'trend': (data[-1]['sleep']['quality'] - data[0]['sleep']['quality'])
        }
    }
    
    # Calculate symptom averages
    physical_symptoms = []
    emotional_symptoms = []
    for record in data:
        physical_avg = np.mean(list(record['symptoms']['physical'].values()))
        emotional_avg = np.mean(list(record['symptoms']['emotional'].values()))
        physical_symptoms.append(physical_avg)
        emotional_symptoms.append(emotional_avg)
    
    metrics['symptoms'] = {
        'physical_avg': np.mean(physical_symptoms),
        'emotional_avg': np.mean(emotional_symptoms),
        'physical_trend': physical_symptoms[-1] - physical_symptoms[0],
        'emotional_trend': emotional_symptoms[-1] - emotional_symptoms[0]
    }
    
    return metrics

def render_mood_analysis(data, metrics):
    """Render mood analysis section"""
    st.subheader("😊 Mood Analysis")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Average Mood", f"{metrics['mood']['avg']:.1f}/10", 
                f"{metrics['mood']['trend']:+.1f}")
    col2.metric("Highest Mood", f"{metrics['mood']['max']}/10")
    col3.metric("Lowest Mood", f"{metrics['mood']['min']}/10")
    
    # Mood trend chart
    mood_data = pd.DataFrame([
        {'date': r['date'], 'score': r['mood']['score']} 
        for r in data
    ])
    fig = px.line(mood_data, x='date', y='score', 
                  title="Mood Score Trend",
                  labels={'score': 'Mood Score', 'date': 'Date'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Mood triggers analysis
    col1, col2 = st.columns(2)
    with col1:
        triggers = []
        for r in data:
            triggers.extend(r['mood']['triggers'])
        trigger_counts = pd.Series(triggers).value_counts()
        fig = px.bar(trigger_counts, title="Common Mood Triggers")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Mood distribution
        fig = px.histogram(mood_data['score'], 
                          title="Mood Score Distribution",
                          labels={'value': 'Mood Score'})
        st.plotly_chart(fig, use_container_width=True)

def render_sleep_analysis(data, metrics):
    """Render sleep analysis section"""
    st.subheader("😴 Sleep Analysis")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Average Sleep Quality", f"{metrics['sleep']['avg']:.1f}/10",
                f"{metrics['sleep']['trend']:+.1f}")
    col2.metric("Best Sleep", f"{metrics['sleep']['max']}/10")
    col3.metric("Poorest Sleep", f"{metrics['sleep']['min']}/10")
    
    # Sleep quality trend
    sleep_data = pd.DataFrame([
        {'date': r['date'], 'quality': r['sleep']['quality'],
         'bedtime': r['sleep']['bedtime'], 
         'waketime': r['sleep']['waketime']} 
        for r in data
    ])
    fig = px.line(sleep_data, x='date', y='quality',
                  title="Sleep Quality Trend",
                  labels={'quality': 'Sleep Quality', 'date': 'Date'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Sleep patterns analysis
    col1, col2 = st.columns(2)
    with col1:
        # Sleep issues analysis
        issues = []
        for r in data:
            issues.extend(r['sleep']['issues'])
        issue_counts = pd.Series(issues).value_counts()
        fig = px.bar(issue_counts, title="Common Sleep Issues")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sleep timing patterns
        sleep_times = pd.DataFrame([
            {'date': r['date'], 
             'bedtime': datetime.strptime(r['sleep']['bedtime'], '%H:%M').time(),
             'waketime': datetime.strptime(r['sleep']['waketime'], '%H:%M').time()}
            for r in data
        ])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=sleep_times['date'], 
                                y=[t.strftime('%H:%M') for t in sleep_times['bedtime']],
                                name='Bedtime'))
        fig.add_trace(go.Scatter(x=sleep_times['date'], 
                                y=[t.strftime('%H:%M') for t in sleep_times['waketime']],
                                name='Wake time'))
        fig.update_layout(title="Sleep Timing Patterns")
        st.plotly_chart(fig, use_container_width=True)

def render_symptoms_analysis(data, metrics):
    """Render symptoms analysis section"""
    st.subheader("🌡️ Symptoms Analysis")
    
    # Key metrics
    col1, col2 = st.columns(2)
    col1.metric("Avg Physical Symptoms", f"{metrics['symptoms']['physical_avg']:.1f}/10",
                f"{metrics['symptoms']['physical_trend']:+.1f}")
    col2.metric("Avg Emotional Symptoms", f"{metrics['symptoms']['emotional_avg']:.1f}/10",
                f"{metrics['symptoms']['emotional_trend']:+.1f}")
    
    # Physical symptoms trend
    physical_data = []
    for r in data:
        for symptom, intensity in r['symptoms']['physical'].items():
            physical_data.append({
                'date': r['date'],
                'symptom': symptom,
                'intensity': intensity
            })
    df_physical = pd.DataFrame(physical_data)
    fig = px.line(df_physical, x='date', y='intensity', color='symptom',
                  title="Physical Symptoms Over Time")
    st.plotly_chart(fig, use_container_width=True)
    
    # Emotional symptoms trend
    emotional_data = []
    for r in data:
        for symptom, intensity in r['symptoms']['emotional'].items():
            emotional_data.append({
                'date': r['date'],
                'symptom': symptom,
                'intensity': intensity
            })
    df_emotional = pd.DataFrame(emotional_data)
    fig = px.line(df_emotional, x='date', y='intensity', color='symptom',
                  title="Emotional Symptoms Over Time")
    st.plotly_chart(fig, use_container_width=True)
    
    # Symptom correlation analysis
    col1, col2 = st.columns(2)
    with col1:
        # Average symptom intensities
        avg_physical = df_physical.groupby('symptom')['intensity'].mean()
        fig = px.bar(avg_physical, title="Average Physical Symptom Intensities")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Average emotional intensities
        avg_emotional = df_emotional.groupby('symptom')['intensity'].mean()
        fig = px.bar(avg_emotional, title="Average Emotional Symptom Intensities")
        st.plotly_chart(fig, use_container_width=True)

async def main():
    period = render_user_info()
    
    st.title("Health Analysis & Progress Report")
    st.markdown(f"""
    Detailed analysis of your health patterns over the past {period}, highlighting trends,
    improvements, and areas needing attention.
    """)
    
    data = data_store.get_data_for_period(period)
    if data.empty:
        st.warning("No data available for the selected period")
        return

    data = data.to_dict('records')
    latest = data[-1] if data else None
    
    if data:
        metrics = calculate_metrics(data)
        
        # Create tabs for different analyses
        tab_names = ["mood", "sleep", "symptoms"]
        selected_tab = st.tabs([
            "😊 Mood Analysis",
            "😴 Sleep Analysis",
            "🌡️ Symptoms Analysis"
        ])
        
        # Track which tab is active
        for i, tab in enumerate(selected_tab):
            with tab:
                if i == 0:
                    render_mood_analysis(data, metrics)
                    current_tab = "mood"
                elif i == 1:
                    render_sleep_analysis(data, metrics)
                    current_tab = "sleep"
                elif i == 2:
                    render_symptoms_analysis(data, metrics)
                    current_tab = "symptoms"
                
                # AI Insights for current tab only
                with st.spinner("Generating AI insights..."):
                    insights = await gemini_api.analyze_dashboard_data({
                        "current_data": data[-1],
                        "historical_data": data,
                        "period": period
                    }, period)
                    
                    if insights and "component_insights" in insights:
                        st.header("🤖 AI Health Insights")
                        analysis = insights["component_insights"].get(current_tab)
                        
                        if analysis:
                            st.write(f"**Status:** {analysis.get('status', '')}")
                            st.write(f"**Quick Review:** {analysis.get('quick_review', '')}")
                            st.write("**Recommendations:**")
                            for rec in analysis.get('recommendations', []):
                                st.success(f"• {rec}")
    else:
        st.warning("No health data available for the selected period.")

if __name__ == "__main__":
    asyncio.run(main())