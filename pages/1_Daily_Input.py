import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.express as px
import plotly.graph_objects as go
import asyncio
import sys
from pathlib import Path

# Add the project root directory to Python path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from utils.data_store import data_store
from utils.gemini_api import gemini_api

# Page configuration
st.set_page_config(
    page_title="MenoCare - Daily Health Input",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data store
data_store.initialize_session_state()

def render_user_info():
    """Display user information in sidebar"""
    user = st.session_state.user_data
    st.sidebar.image("https://api.dicebear.com/7.x/micah/svg?seed=Jane&mood=happy&smile=true", width=150)
    st.sidebar.title(f"👋 Welcome, {user['name']}")
    st.sidebar.markdown(f"""
    #### Personal Information
    - 🎂 Age: {user['age']} years
    - 📅 Menopause Stage: {user['menopause_stage']}
    - 🕒 Last Updated: {user['last_update']}
    """)

async def process_module_submission(module_type: str, current_data: dict, container):
    """Process module data submission and analysis"""
    try:
        # Save data
        data_store.add_health_record(current_data)
        
        # Show success message in the container
        container.success(f"{module_type.capitalize()} data saved successfully!")
        container.balloons()
        
        # Get historical data for analysis
        historical_data = data_store.get_recent_records()
        
        # Prepare module-specific data
        module_data = {
            "current_data": current_data[module_type.lower()],
            "historical_data": [record[module_type.lower()] for record in historical_data],
            "module_type": module_type.lower()
        }
        
        # Generate and show analysis
        with st.spinner(f'Analyzing your {module_type.lower()} data...'):
            analysis = await gemini_api.analyze_daily_input(module_data)
            
            if analysis:
                # Show analysis results
                if analysis.get("today_insights"):
                    container.subheader(f"🔍 Today's {module_type} Analysis")
                    for insight in analysis["today_insights"]:
                        container.info(insight)
                
                if analysis.get("recommendations"):
                    container.subheader(f"💡 {module_type} Recommendations")
                    for rec in analysis["recommendations"]:
                        container.success(rec)
            else:
                container.warning("Unable to generate analysis at this time.")
                
    except Exception as e:
        container.error(f"Error processing {module_type.lower()} data: {str(e)}")
        with container.expander("Debug Info"):
            container.write(e)

def mood_module():
    """Mood tracking module"""
    st.header("😊 Mood Module")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.slider(
            "How are you feeling today? (1-10)",
            min_value=1,
            max_value=10,
            value=7,
            help="1 = Very low, 10 = Excellent",
            key="mood_score"
        )
        
        st.multiselect(
            "What factors influenced your mood today?",
            options=[
                "Work Stress",
                "Family Matters",
                "Physical Discomfort",
                "Sleep Quality",
                "Social Interactions",
                "Weather",
                "Exercise",
                "Other"
            ],
            key="mood_triggers"
        )
        
        if "Other" in st.session_state.get("mood_triggers", []):
            st.text_input(
                "Please specify other mood triggers:",
                key="mood_notes"
            )
    
    with col2:
        try:
            df = data_store.get_data_for_period('week')
            if not df.empty:
                fig = px.line(df, x='date', y='mood_score',
                         title="Your Recent Mood Trend",
                         labels={'mood_score': 'Mood Score', 'date': 'Date'})
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No historical mood data available yet")
        except Exception as e:
            st.warning("Unable to load mood trend")

def sleep_module():
    """Sleep tracking module"""
    st.header("😴 Sleep Module")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.time_input(
            "What time did you go to bed?",
            time(22, 0),
            key="bedtime"
        )
        st.time_input(
            "What time did you wake up?",
            time(7, 0),
            key="waketime"
        )
        
        st.slider(
            "Rate your sleep quality (1-10)",
            min_value=1,
            max_value=10,
            value=7,
            help="1 = Poor, 10 = Excellent",
            key="sleep_quality"
        )
    
    with col2:
        st.multiselect(
            "Did you experience any sleep issues?",
            options=[
                "Difficulty Falling Asleep",
                "Waking Up During Night",
                "Early Morning Awakening",
                "Night Sweats",
                "Disturbing Dreams",
                "None"
            ],
            default=["None"],
            key="sleep_issues"
        )
        
        if "None" not in st.session_state.get("sleep_issues", []):
            st.number_input(
                "How many times did you wake up during the night?",
                min_value=0,
                max_value=10,
                value=0,
                key="wake_frequency"
            )
        
        try:
            df = data_store.get_data_for_period('week')
            if not df.empty:
                fig = px.line(df, x='date', y='sleep_quality',
                         title="Your Sleep Quality Trend",
                         labels={'sleep_quality': 'Sleep Score', 'date': 'Date'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No historical sleep data available yet")
        except Exception as e:
            st.warning("Unable to load sleep trend")

def symptoms_module():
    """Symptoms tracking module"""
    st.header("🌡️ Symptoms Module")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Physical Symptoms")
        st.slider("Hot Flashes Intensity", 0, 10, 0, key="hot_flashes")
        st.slider("Night Sweats Intensity", 0, 10, 0, key="night_sweats")
        st.slider("Headache Intensity", 0, 10, 0, key="headaches")
        st.slider("Joint Pain Intensity", 0, 10, 0, key="joint_pain")
    
    with col2:
        st.subheader("Emotional Symptoms")
        st.slider("Anxiety Level", 0, 10, 0, key="anxiety")
        st.slider("Irritability Level", 0, 10, 0, key="irritability")
        st.slider("Mood Swing Intensity", 0, 10, 0, key="mood_swings")
        st.slider("Energy Level", 0, 10, 5, key="energy_level")
    
    st.subheader("Other Symptoms")
    st.text_area(
        "Any other symptoms you'd like to note?",
        placeholder="Describe any other symptoms...",
        key="other_symptoms"
    )

def diet_module():
    """Diet tracking module"""
    st.header("🍽️ Diet Module")
    
    # Create tabs for each meal
    meal_tabs = st.tabs(["Breakfast", "Lunch", "Dinner", "Snacks"])
    
    for i, meal_tab in enumerate(meal_tabs):
        with meal_tab:
            meal_name = ["Breakfast", "Lunch", "Dinner", "Snacks"][i]
            st.subheader(f"{meal_name} Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.multiselect(
                    "Food Categories",
                    options=[
                        "High Protein",
                        "High Fiber",
                        "High Sugar",
                        "High Fat",
                        "Balanced",
                        "Vegetables",
                        "Fruits",
                        "Dairy",
                        "Grains"
                    ],
                    key=f"food_cat_{meal_name}"
                )
            
            with col2:
                st.text_area(
                    "Meal Notes",
                    placeholder=f"Describe your {meal_name.lower()}...",
                    key=f"meal_notes_{meal_name}"
                )
    
    # Additional dietary information
    st.subheader("General Dietary Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input(
            "Water intake (glasses)",
            min_value=0,
            max_value=20,
            value=6,
            key="water_intake"
        )
        
        st.number_input(
            "Caffeine intake (cups)",
            min_value=0,
            max_value=10,
            value=2,
            key="caffeine_intake"
        )
    
    with col2:
        st.multiselect(
            "Supplements taken today",
            options=[
                "Calcium",
                "Vitamin D",
                "Magnesium",
                "Fish Oil",
                "Multivitamin",
                "Iron",
                "Other"
            ],
            key="supplements"
        )

def collect_form_data() -> dict:
    """Collect form data in a structured format"""
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "mood": {
            "score": st.session_state.get("mood_score", 7),
            "triggers": st.session_state.get("mood_triggers", []),
            "notes": st.session_state.get("mood_notes", "")
        },
        "sleep": {
            "bedtime": st.session_state.get("bedtime").strftime("%H:%M") if isinstance(st.session_state.get("bedtime"), time) else "22:00",
            "waketime": st.session_state.get("waketime").strftime("%H:%M") if isinstance(st.session_state.get("waketime"), time) else "07:00",
            "quality": st.session_state.get("sleep_quality", 7),
            "issues": st.session_state.get("sleep_issues", []),
            "wake_frequency": st.session_state.get("wake_frequency", 0)
        },
        "diet": {
            "meals": {
                "breakfast": {
                    "categories": st.session_state.get("food_cat_Breakfast", []),
                    "notes": st.session_state.get("meal_notes_Breakfast", "")
                },
                "lunch": {
                    "categories": st.session_state.get("food_cat_Lunch", []),
                    "notes": st.session_state.get("meal_notes_Lunch", "")
                },
                "dinner": {
                    "categories": st.session_state.get("food_cat_Dinner", []),
                    "notes": st.session_state.get("meal_notes_Dinner", "")
                },
                "snacks": {
                    "categories": st.session_state.get("food_cat_Snacks", []),
                    "notes": st.session_state.get("meal_notes_Snacks", "")
                }
            },
            "water_intake": st.session_state.get("water_intake", 6),
            "caffeine_intake": st.session_state.get("caffeine_intake", 2),
            "supplements": st.session_state.get("supplements", [])
        },
        "symptoms": {
            "physical": {
                "hot_flashes": st.session_state.get("hot_flashes", 0),
                "night_sweats": st.session_state.get("night_sweats", 0),
                "headaches": st.session_state.get("headaches", 0),
                "joint_pain": st.session_state.get("joint_pain", 0)
            },
            "emotional": {
                "anxiety": st.session_state.get("anxiety", 0),
                "irritability": st.session_state.get("irritability", 0),
                "mood_swings": st.session_state.get("mood_swings", 0),
                "energy_level": st.session_state.get("energy_level", 5)
            },
            "notes": st.session_state.get("other_symptoms", "")
        }
    }

def main():
    render_user_info()
    
    st.title("Daily Health Check-In")
    st.markdown("""
    Please take a moment to record your daily health metrics. This information helps us 
    provide better personalized recommendations and track your progress.
    """)
    
    # Create tabs for each module
    tab1, tab2, tab3, tab4 = st.tabs([
        "😊 Mood",
        "😴 Sleep",
        "🌡️ Symptoms",
        "🍽️ Diet"
    ])
    
    # Mood tab
    with tab1:
        mood_module()
        # Create container for mood results
        mood_container = st.container()
        with st.form(key="mood_form"):
            submit_mood = st.form_submit_button(
                "Save Mood Record",
                type="primary",
                use_container_width=True
            )
            if submit_mood:
                # Clear previous results by creating a new container
                mood_container.empty()
                current_data = collect_form_data()
                asyncio.run(process_module_submission("Mood", current_data, mood_container))
    
    # Sleep tab
    with tab2:
        sleep_module()
        # Create container for sleep results
        sleep_container = st.container()
        with st.form(key="sleep_form"):
            submit_sleep = st.form_submit_button(
                "Save Sleep Record",
                type="primary",
                use_container_width=True
            )
            if submit_sleep:
                # Clear previous results by creating a new container
                sleep_container.empty()
                current_data = collect_form_data()
                asyncio.run(process_module_submission("Sleep", current_data, sleep_container))
    
    # Symptoms tab
    with tab3:
        symptoms_module()
        # Create container for symptoms results
        symptoms_container = st.container()
        with st.form(key="symptoms_form"):
            submit_symptoms = st.form_submit_button(
                "Save Symptoms Record",
                type="primary",
                use_container_width=True
            )
            if submit_symptoms:
                # Clear previous results by creating a new container
                symptoms_container.empty()
                current_data = collect_form_data()
                asyncio.run(process_module_submission("Symptoms", current_data, symptoms_container))
    
    # Diet tab
    with tab4:
        diet_module()
        # Create container for diet results
        diet_container = st.container()
        with st.form(key="diet_form"):
            submit_diet = st.form_submit_button(
                "Save Diet Record",
                type="primary",
                use_container_width=True
            )
            if submit_diet:
                # Clear previous results by creating a new container
                diet_container.empty()
                current_data = collect_form_data()
                asyncio.run(process_module_submission("Diet", current_data, diet_container))

    # Update last update time if any form was submitted
    if submit_mood or submit_sleep or submit_symptoms or submit_diet:
        st.session_state.user_data['last_update'] = datetime.now().strftime("%Y-%m-%d")

if __name__ == "__main__":
    main()