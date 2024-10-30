import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_store import data_store
from utils.gemini_api import gemini_api
import asyncio

# Page configuration
st.set_page_config(
    page_title="MenoCare - Health Education",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data store
data_store.initialize_session_state()

def render_sidebar():
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

def get_default_content(topic):
    """Get default content when API fails"""
    return {
        "explanation": f"""
        {topic} is an important aspect of menopause management. While we're unable to 
        provide personalized content at the moment, please consider consulting our general 
        resources or your healthcare provider.
        """,
        "relevance": "Your experience is unique. Understanding your symptoms helps in managing them effectively.",
        "evidence": [
            "Regular monitoring helps track symptom patterns",
            "Lifestyle modifications can help manage symptoms",
            "Each person's menopause journey is different"
        ],
        "strategies": [
            "Keep a symptom diary",
            "Stay in regular contact with your healthcare provider",
            "Maintain a healthy lifestyle with regular exercise and balanced diet"
        ],
        "medical_attention": [
            "If symptoms significantly affect your daily life",
            "For any concerning changes in your health"
        ]
    }

async def render_personalized_content(topic: str = None):
    """Render personalized educational content"""
    st.header("📚 Personalized Educational Content")
    
    try:
        recent_records = data_store.get_recent_records()
        user_data = st.session_state.user_data
        
        # Prepare API request data
        topic_data = {
            "topic": topic,
            "user": {
                "age": user_data['age'],
                "stage": user_data['menopause_stage'],
                "recent_data": recent_records[-7:] if recent_records else []
            }
        }
        
        # Get personalized content from API
        with st.spinner('Loading personalized content...'):
            try:
                content = await gemini_api.get_health_education(topic, topic_data)
            except Exception as api_error:
                st.warning("Unable to get personalized content. Showing general information.")
                content = get_default_content(topic)
        
        # Display content sections
        if content:
            # Main explanation with proper error handling
            st.markdown(f"### Understanding {topic}")
            st.write(content.get("explanation", "Information not available"))
            
            # Personal relevance in a highlighted box
            if content.get("relevance"):
                st.info("👤 **Personal Relevance**\n\n" + content["relevance"])
            
            # Create two columns for evidence and strategies
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔬 Research & Evidence")
                evidence = content.get("evidence", [])
                if evidence:
                    for item in evidence:
                        st.markdown(f"• {item}")
                else:
                    st.write("Research data not available at the moment.")
            
            with col2:
                st.subheader("💡 Management Strategies")
                strategies = content.get("strategies", [])
                if strategies:
                    for strategy in strategies:
                        st.success(f"• {strategy}")
                else:
                    st.write("Strategy recommendations not available at the moment.")
            
            # Medical attention warnings in a separate section
            if content.get("medical_attention"):
                st.subheader("⚠️ When to Seek Medical Attention")
                for warning in content["medical_attention"]:
                    st.warning(warning)
        
    except Exception as e:
        st.error("An error occurred while loading the content.")
        with st.expander("Debug Info"):
            st.write(f"Error: {str(e)}")
        content = get_default_content(topic)
        st.warning("Showing general information instead of personalized content.")
        st.write(content["explanation"])

def render_topic_selection():
    """Render topic selection section"""
    st.header("🔍 Explore Topics")
    
    topics = [
        "Managing Hot Flashes",
        "Sleep Improvement",
        "Mood Management",
        "Hormone Changes",
        "Exercise & Fitness",
        "Nutrition Guidelines"
    ]
    
    selected_topic = st.selectbox(
        "What would you like to learn about?",
        topics,
        key="selected_topic",
        index=0  # Set default selection to first topic
    )
    
    return selected_topic

async def main():
    try:
        render_sidebar()
        
        st.title("Health Education & Empowerment")
        st.markdown("""
        Access personalized health information and evidence-based guidance 
        for managing your menopause journey effectively.
        """)
        
        # Topic selection
        selected_topic = render_topic_selection()
        st.divider()
        
        # Render personalized content for selected topic
        await render_personalized_content(selected_topic)
        
        # Quick Tips Section
        st.divider()
        st.header("💡 Quick Tips")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("""
            **Daily Wellness Practice**
            
            Try this 4-7-8 breathing technique:
            1. Inhale for 4 seconds
            2. Hold for 7 seconds
            3. Exhale for 8 seconds
            
            Practice this when feeling stressed or before bed.
            """)
            
        with col2:
            st.success("""
            **Remember**
            
            • Stay hydrated throughout the day
            • Maintain regular exercise routine
            • Keep a consistent sleep schedule
            • Track your symptoms regularly
            """)
    
    except Exception as e:
        st.error("An unexpected error occurred.")
        with st.expander("Debug Info"):
            st.write(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())