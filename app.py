import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import os
import io

# Load the API key from .env
load_dotenv()
api_key = os.getenv("my_api_key")
genai.configure(api_key=api_key)

# Function to get meal preference response
def get_meal_preference_response(meal_type, intake_type, cuisine, goal, duration):
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
    prompt = f"Generate a {meal_type} meal plan for {duration} days with a {intake_type} intake, focusing on {cuisine} cuisine for the goal of {goal}."
    response = model.generate_content(prompt)
    return response.text

# Function to process general query (text/image)
def get_general_query_response(input_text, uploaded_image=None, use_image=False):
    if use_image and uploaded_image is not None:
        
        pil_image = Image.open(uploaded_image)
        pil_image = pil_image.resize((224, 224))
        img_bytes = io.BytesIO()
        pil_image.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()

        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        response = model.generate_content([input_text, pil_image])
    else:
        model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
        response = model.generate_content(input_text)
    return response.text

# Streamlit UI
st.set_page_config(page_title="Gemini Nutrition_App 🥗", layout="centered")
st.title("🥗 Gemini Nutrition_App - Your Personalized Nutrition Assistant")

tab1, tab2 = st.tabs(["📋 Meal Plan Generator", "🧠 General Query + Calorie Count"])

# -------- Tab 1: Meal Plan Generator --------
with tab1:
    st.header("Customize Your Meal Plan")
    meal_type = st.selectbox("Select Meal Type", ["Breakfast", "Lunch", "Dinner", "Full Day"])
    intake_type = st.selectbox("Select Intake Type", ["Low Carb", "High Protein", "Balanced", "Low Sugar"])
    cuisine = st.selectbox("Choose Cuisine", ["Indian", "Mediterranean", "Asian", "Western", "Vegetarian"])
    goal = st.selectbox("Health Goal", ["Lose Weight", "Gain Weight", "Maintain Weight", "Diabetes Management"])
    duration = st.slider("Duration (in Days)", 1, 30, 7)

    if st.button("Generate Meal Plan"):
        result = get_meal_preference_response(meal_type, intake_type, cuisine, goal, duration)
        st.success("Meal Plan Generated ✅")
        st.text_area("Your Personalized Meal Plan", result, height=300)

# -------- Tab 2: General Query or Calorie Count from Image --------
with tab2:
    st.header("Ask a Nutrition Question or Analyze Food Image")
    input_text = st.text_input("Enter your question or description (e.g., 'How many calories in this meal?')")

    uploaded_file = st.file_uploader("Upload food image (optional)", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("Submit Query"):
        use_image = uploaded_file is not None
        result = get_general_query_response(input_text, uploaded_file, use_image)
        st.subheader("AI Response")
        st.write(result)
