import streamlit as st
import pickle
import numpy as np
from fpdf import FPDF
import google.generativeai as genai

# ---------- Load model ----------
with open('best_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

# ---------- Guideline text (fed to the AI correction layer) ----------
GUIDELINES = """
Diabetic dietary guidelines (summary):
- Prefer low glycemic index (GI) foods: millets (bajra, jowar, ragi), whole grains, legumes.
- Bajra, jowar, ragi are LOW GI and fiber-rich, generally favorable for diabetics despite being carbs.
- Refined sugar, white rice, maida-based foods: high GI, should be limited.
- Jaggery in small quantities (under 5-10g) has a lower glycemic impact than refined sugar but is still a sugar - moderate, not forbidden.
- Ghee and healthy fats in moderate quantity (1 tsp) are acceptable, not inherently "unhealthy."
- Portion size matters more than a single ingredient being "good" or "bad."
- Fiber-rich vegetables and protein help slow glucose absorption when eaten with carbs.
"""

# ---------- Baseline prediction ----------
def baseline_predict(glucose, bmi, age, bp):
    features = np.array([[1, glucose, bp, 20, 80, bmi, 0.5, age]])
    scaled = scaler.transform(features)
    pred = model.predict(scaled)[0]
    prob = model.predict_proba(scaled)[0][1]
    return pred, prob

# ---------- DEBUG: list available models (temporary) ----------
with st.expander("DEBUG: Available Gemini models (click to check)"):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                st.write(m.name)
    except Exception as e:
        st.write(f"Error listing models: {e}")

# ---------- AI correction layer ----------
def ai_correct(food_item, baseline_verdict, prob, user_profile):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model_ai = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""You are a nutritionist agent. A baseline ML model gave this raw verdict
for a user's diabetes risk: {'HIGH RISK' if baseline_verdict==1 else 'LOW RISK'} (probability: {prob:.2f}).

User profile: {user_profile}
Food item being evaluated: {food_item}

Dietary guidelines to use as reference:
{GUIDELINES}

Task: Give a corrected, context-aware dietary assessment of this food item for this user.
Explain briefly WHY the baseline model's raw signal might be misleading (if applicable),
using the guidelines above. Keep it concise (under 150 words). End with a one-line practical recommendation.
"""
    response = model_ai.generate_content(prompt)
    return response.text

# ---------- PDF generation ----------
def generate_pdf(user_profile, food_item, baseline_text, ai_text):
    pdf = FPDF()
    pdf.add_page()
