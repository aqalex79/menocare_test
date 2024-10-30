import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

def test_gemini():
    st.title("Test Gemini API Integration")
    
    # Test prompt
    test_prompt = """
    Analyze this sample menopause symptom data:
    {
        "mood": 7,
        "sleep_quality": 6,
        "hot_flashes": 3,
        "symptoms": ["mild anxiety", "occasional hot flashes"]
    }
    
    Provide brief health insights and recommendations.
    """
    
    if st.button("Test API Connection"):
        try:
            with st.spinner("Generating response..."):
                response = model.generate_content(test_prompt)
                st.success("API Connection Successful!")
                st.subheader("Sample Response:")
                st.write(response.text)
        except Exception as e:
            st.error(f"Error connecting to Gemini API: {str(e)}")

# Run the test
if __name__ == "__main__":
    test_gemini()
