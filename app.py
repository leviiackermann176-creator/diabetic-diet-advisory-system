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

# ---------- AI correction layer ----------
def ai_correct(food_item, baseline_verdict, prob, user_profile):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model_ai = genai.GenerativeModel("gemini-2.5-flash")
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
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="Personalized Diabetic Diet Report", ln=True, align='C')
    pdf.set_font("Arial", size=11)
    pdf.ln(10)
    pdf.multi_cell(0, 8, f"User Profile: {user_profile}")
    pdf.multi_cell(0, 8, f"Food Item: {food_item}")
    pdf.ln(5)
    pdf.multi_cell(0, 8, f"Baseline Model Verdict: {baseline_text}")
    pdf.ln(5)
    pdf.multi_cell(0, 8, f"AI-Corrected Assessment:\n{ai_text}")
    path = "diet_report.pdf"
    pdf.output(path)
    return path

# ---------- Streamlit UI ----------
st.title("🩺 Diabetic Diet Advisory System")
st.write("Enter your details and a food item to get a personalized, AI-corrected dietary assessment.")

age = st.number_input("Age", 18, 90, 45)
glucose = st.number_input("Glucose level (mg/dL)", 70, 300, 140)
bmi = st.number_input("BMI", 15.0, 50.0, 25.0)
bp = st.number_input("Blood Pressure", 60, 140, 80)
food_item = st.text_input("Food item eaten (e.g., 'Bajra roti with ghee and jaggery')")

if st.button("Analyze"):
    if food_item.strip() == "":
        st.warning("Please enter a food item.")
    else:
        with st.spinner("Running baseline model..."):
            pred, prob = baseline_predict(glucose, bmi, age, bp)
            baseline_text = f"{'High diabetes risk' if pred==1 else 'Low diabetes risk'} (confidence: {prob:.0%})"
        st.subheader("Baseline ML Model Verdict")
        st.write(baseline_text)

        with st.spinner("Getting AI-corrected assessment..."):
            user_profile = f"Age {age}, Glucose {glucose}, BMI {bmi}, BP {bp}"
            ai_text = ai_correct(food_item, pred, prob, user_profile)
        st.subheader("AI-Corrected Dietary Assessment")
        st.write(ai_text)

        pdf_path = generate_pdf(user_profile, food_item, baseline_text, ai_text)
        with open(pdf_path, "rb") as f:
            st.download_button("Download PDF Report", f, file_name="diet_report.pdf")
