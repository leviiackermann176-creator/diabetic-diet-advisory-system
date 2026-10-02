import streamlit as st
import pickle
import numpy as np
from fpdf import FPDF
from google import genai

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

# ---------- AI correction layer ----------
def ai_correct(food_item, baseline_verdict, prob, user_profile):
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
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
    fallback_models = ["gemini-flash-latest", "gemini-2.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-lite-latest"]
    last_error = None
    for m in fallback_models:
        try:
            response = client.models.generate_content(
                model=m,
                contents=prompt
            )
            return response.text
        except Exception as e:
            last_error = e
            continue
        return "AI correction temporarily unavailable right now. Please try again in a minute."
