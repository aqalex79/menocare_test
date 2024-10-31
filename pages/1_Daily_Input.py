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
    st.sidebar.image("https://api.dicebear.com/7.x/big-ears/svg?seed=Jane&mood=happy", width=150)
    st.sidebar.title(f"👋 Welcome, {user['name']}")
    st.sidebar.markdown(f"""
    #### Personal Information
    - 🎂 Age: {user['age']} years
    - 📅 Menopause Stage: {user['menopause_stage']}
    - 🕒 Last Updated: {user['last_update']}
    """)

async def process_module_submission(module_type: str, current_data: dict, container, meal_type: str = None):
    """Process module data submission and analysis"""
    try:
        # Save data
        data_store.add_health_record(current_data)
        container.empty()  # 清空容器，包括表单和按钮
        
        # Show success message in the container
        message = f"{meal_type} data" if meal_type else f"{module_type.capitalize()} data"
        container.success(f"{message} saved successfully!")
        container.balloons()
        
        # Get historical data for analysis
        historical_data = data_store.get_recent_records()
        
        # Prepare module-specific data
        if module_type.lower() == "diet" and meal_type:
            # 安全地获取历史数据
            historical_meals = []
            for record in historical_data:
                try:
                    if "diet" in record and "meals" in record["diet"]:
                        meal_data = record["diet"]["meals"].get(meal_type.lower(), {})
                        historical_meals.append(meal_data)
                except Exception:
                    continue
                    
            module_data = {
                "current_data": current_data["diet"]["meals"][meal_type.lower()],
                "historical_data": historical_meals,
                "module_type": module_type.lower(),
                "meal_type": meal_type.lower()
            }
        else:
            module_data = {
                "current_data": current_data[module_type.lower()],
                "historical_data": [record[module_type.lower()] for record in historical_data if module_type.lower() in record],
                "module_type": module_type.lower()
            }
        
        # Generate and show analysis
        with st.spinner(f'Analyzing your {message.lower()}...'):
            analysis = await gemini_api.analyze_daily_input(module_data)
            
            if analysis:
                # Show analysis results
                if analysis.get("today_insights"):
                    container.subheader(f"🔍 Today's {meal_type if meal_type else module_type} Analysis")
                    for insight in analysis["today_insights"]:
                        container.info(insight)
                
                if analysis.get("recommendations"):
                    container.subheader(f"💡 {meal_type if meal_type else module_type} Recommendations")
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
    
    meal_tabs = st.tabs(["Breakfast", "Lunch", "Dinner", "Snacks"])
    
    for i, meal_tab in enumerate(meal_tabs):
        with meal_tab:
            meal_name = ["Breakfast", "Lunch", "Dinner", "Snacks"][i]
            st.subheader(f"{meal_name} Details")
            
            # Meal specific information
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
                
                st.text_area(
                    "Meal Notes",
                    placeholder=f"Describe your {meal_name.lower()}...",
                    key=f"meal_notes_{meal_name}"
                )
            
            with col2:
                st.number_input(
                    "Water intake (glasses)",
                    min_value=0,
                    max_value=20,
                    value=6,
                    key=f"water_intake_{meal_name}"
                )
                
                st.number_input(
                    "Caffeine intake (cups)",
                    min_value=0,
                    max_value=10,
                    value=2,
                    key=f"caffeine_intake_{meal_name}"
                )
                
                st.multiselect(
                    "Supplements taken",
                    options=[
                        "Calcium",
                        "Vitamin D",
                        "Magnesium",
                        "Fish Oil",
                        "Multivitamin",
                        "Iron",
                        "Other"
                    ],
                    key=f"supplements_{meal_name}"
                )
                
            # 修改表单部分
            meal_container = st.container()
            with meal_container:  # 把form放在container里面
                with st.form(key=f"diet_form_{meal_name.lower()}"):
                    submit_meal = st.form_submit_button(
                        f"Save {meal_name} Record",
                        type="primary",
                        use_container_width=True
                    )
                    if submit_meal:
                        meal_container.empty()
                        current_data = collect_form_data(meal_name)
                        asyncio.run(process_module_submission(
                            "Diet",
                            current_data,
                            meal_container,
                            meal_name
                        ))
                        st.session_state.user_data['last_update'] = datetime.now().strftime("%Y-%m-%d")

def collect_form_data(current_meal: str = None) -> dict:
    """Collect form data in a structured format"""
    data = {
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
    
    # Add diet data only if current_meal is provided
    if current_meal:
        data["diet"] = {
            "meals": {
                current_meal.lower(): {
                    "categories": st.session_state.get(f"food_cat_{current_meal}", []),
                    "notes": st.session_state.get(f"meal_notes_{current_meal}", "")
                }
            },
            "water_intake": st.session_state.get(f"water_intake_{current_meal}", 6),
            "caffeine_intake": st.session_state.get(f"caffeine_intake_{current_meal}", 2),
            "supplements": st.session_state.get(f"supplements_{current_meal}", [])
        }
    
    return data

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
        mood_container = st.container()
        with mood_container:  # 把form放在container里面
            with st.form(key="mood_form"):
                submit_mood = st.form_submit_button(
                    "Save Mood Record",
                    type="primary",
                    use_container_width=True
                )
                if submit_mood:
                    mood_container.empty()
                    current_data = collect_form_data()
                    asyncio.run(process_module_submission("Mood", current_data, mood_container))

    # Sleep tab
    with tab2:
        sleep_module()
        sleep_container = st.container()
        with sleep_container:  # 把form放在container里面
            with st.form(key="sleep_form"):
                submit_sleep = st.form_submit_button(
                    "Save Sleep Record",
                    type="primary",
                    use_container_width=True
                )
                if submit_sleep:
                    sleep_container.empty()
                    current_data = collect_form_data()
                    asyncio.run(process_module_submission("Sleep", current_data, sleep_container))

    # Symptoms tab
    with tab3:
        symptoms_module()
        symptoms_container = st.container()
        with symptoms_container:  # 把form放在container里面
            with st.form(key="symptoms_form"):
                submit_symptoms = st.form_submit_button(
                    "Save Symptoms Record",
                    type="primary",
                    use_container_width=True
                )
                if submit_symptoms:
                    symptoms_container.empty()
                    current_data = collect_form_data()
                    asyncio.run(process_module_submission("Symptoms", current_data, symptoms_container))
        # Diet tab
    with tab4:
        diet_module()
    
if __name__ == "__main__":
    main()