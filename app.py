import streamlit as st
import pickle
import numpy as np
from fpdf import FPDF
from google import genai
import hashlib
import hmac
import secrets
import sqlite3
from datetime import datetime
import html
import os
import textwrap


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Diabetic Diet Advisory",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DATABASE
# ============================================================

DB_FILE = "patient_history.db"


def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # User accounts
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    # Patient profiles
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            username TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            diabetes_type TEXT,
            glucose REAL,
            bmi REAL,
            blood_pressure REAL,
            dietary_preference TEXT,
            allergies TEXT,
            activity_level TEXT,
            created_at TEXT,
            FOREIGN KEY(username) REFERENCES users(username)
        )
        """
    )

    # Meal history
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS meal_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            food_item TEXT NOT NULL,
            glucose REAL,
            bmi REAL,
            blood_pressure REAL,
            baseline_verdict TEXT,
            probability REAL,
            ai_assessment TEXT,
            created_at TEXT,
            FOREIGN KEY(username) REFERENCES users(username)
        )
        """
    )

    conn.commit()
    conn.close()


init_database()


# ============================================================
# PASSWORD SECURITY
# ============================================================

def hash_password(password: str) -> str:
    """Create a salted PBKDF2 password hash."""
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000,
    )
    return f"{salt.hex()}${password_hash.hex()}"


def verify_password(password: str, stored_value: str) -> bool:
    """Verify a password against salt$hash stored in the database."""
    try:
        salt_hex, stored_hash_hex = stored_value.split("$", 1)
        salt = bytes.fromhex(salt_hex)

        entered_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            200_000,
        ).hex()

        return hmac.compare_digest(entered_hash, stored_hash_hex)
    except (ValueError, TypeError):
        return False


def username_exists(username: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM users WHERE username = ?",
        (username,),
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def create_user(
    username: str,
    password: str,
    name: str,
    age: int,
    diabetes_type: str,
    glucose: float,
    bmi: float,
    blood_pressure: float,
    dietary_preference: str,
    allergies: str,
    activity_level: str,
):
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, created_at)
            VALUES (?, ?, ?)
            """,
            (username, hash_password(password), now),
        )

        cursor.execute(
            """
            INSERT INTO patients (
                username,
                name,
                age,
                diabetes_type,
                glucose,
                bmi,
                blood_pressure,
                dietary_preference,
                allergies,
                activity_level,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                name,
                age,
                diabetes_type,
                glucose,
                bmi,
                blood_pressure,
                dietary_preference,
                allergies,
                activity_level,
                now,
            ),
        )

        conn.commit()
        return True, None

    except sqlite3.IntegrityError:
        conn.rollback()
        return False, "That username is already registered."

    except Exception as error:
        conn.rollback()
        return False, str(error)

    finally:
        conn.close()


def authenticate_user(username: str, password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        (username,),
    )
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return False

    return verify_password(password, result[0])


# ============================================================
# PATIENT DATABASE FUNCTIONS
# ============================================================

def get_patient(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            username,
            name,
            age,
            diabetes_type,
            glucose,
            bmi,
            blood_pressure,
            dietary_preference,
            allergies,
            activity_level,
            created_at
        FROM patients
        WHERE username = ?
        """,
        (username,),
    )

    result = cursor.fetchone()
    conn.close()
    return result


def save_patient_profile(
    username,
    name,
    age,
    diabetes_type,
    glucose,
    bmi,
    blood_pressure,
    dietary_preference,
    allergies,
    activity_level,
):
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT OR REPLACE INTO patients (
            username,
            name,
            age,
            diabetes_type,
            glucose,
            bmi,
            blood_pressure,
            dietary_preference,
            allergies,
            activity_level,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            username,
            name,
            age,
            diabetes_type,
            glucose,
            bmi,
            blood_pressure,
            dietary_preference,
            allergies,
            activity_level,
            now,
        ),
    )

    conn.commit()
    conn.close()


def update_patient_profile(
    username,
    name,
    age,
    diabetes_type,
    glucose,
    bmi,
    blood_pressure,
    dietary_preference,
    allergies,
    activity_level,
):
    """Update the editable patient information for an existing account."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE patients
        SET
            name = ?,
            age = ?,
            diabetes_type = ?,
            glucose = ?,
            bmi = ?,
            blood_pressure = ?,
            dietary_preference = ?,
            allergies = ?,
            activity_level = ?
        WHERE username = ?
        """,
        (
            name,
            age,
            diabetes_type,
            glucose,
            bmi,
            blood_pressure,
            dietary_preference,
            allergies,
            activity_level,
            username,
        ),
    )

    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def save_meal_history(
    username,
    food_item,
    glucose,
    bmi,
    blood_pressure,
    baseline_verdict,
    probability,
    ai_assessment,
):
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO meal_history (
            username,
            food_item,
            glucose,
            bmi,
            blood_pressure,
            baseline_verdict,
            probability,
            ai_assessment,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            username,
            food_item,
            glucose,
            bmi,
            blood_pressure,
            baseline_verdict,
            probability,
            ai_assessment,
            now,
        ),
    )

    conn.commit()
    conn.close()


def get_meal_history(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            food_item,
            glucose,
            bmi,
            blood_pressure,
            baseline_verdict,
            probability,
            ai_assessment,
            created_at
        FROM meal_history
        WHERE username = ?
        ORDER BY id DESC
        """,
        (username,),
    )

    results = cursor.fetchall()
    conn.close()
    return results


# ============================================================
# MODEL LOADING
# ============================================================

@st.cache_resource
def load_models():
    with open("best_model.pkl", "rb") as f:
        model = pickle.load(f)

    with open("scaler.pkl", "rb") as f:
        scaler = pickle.load(f)

    return model, scaler


model, scaler = load_models()


# ============================================================
# DIETARY GUIDELINES
# ============================================================

GUIDELINES = """
Diabetic dietary guidelines:

- Prefer low glycemic index foods such as millets,
  whole grains and legumes.

- Bajra, jowar and ragi are fiber-rich carbohydrate sources.

- Refined sugar, white rice and maida-based foods should
  generally be limited.

- Jaggery is still a source of sugar and should be used
  moderately.

- Ghee and healthy fats can be used in moderate quantities.

- Portion size matters.

- Fiber-rich vegetables and protein can help slow
  carbohydrate absorption when eaten with carbohydrates.

- Consider the complete meal rather than judging one
  ingredient in isolation.
"""


# ============================================================
# BASELINE ML PREDICTION
# ============================================================

def baseline_predict(glucose, bmi, age, bp):
    features = np.array(
        [[1, glucose, bp, 20, 80, bmi, 0.5, age]]
    )

    scaled = scaler.transform(features)

    pred = model.predict(scaled)[0]

    prob = model.predict_proba(scaled)[0][1]

    return pred, prob


# ============================================================
# GEMINI AI CORRECTION
# ============================================================

def ai_correct(food_item, baseline_verdict, prob, user_profile):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        return (
            "AI correction is unavailable because "
            "GEMINI_API_KEY is not configured in Streamlit Secrets."
        )

    try:
        client = genai.Client(api_key=api_key)
    except Exception:
        return "AI correction is temporarily unavailable. Please try again later."

    prompt = f"""
You are a nutritionist agent assisting an educational
diabetic dietary advisory application.

Baseline ML result:
{'HIGHER-RISK MODEL SIGNAL' if baseline_verdict == 1 else 'LOWER-RISK MODEL SIGNAL'}

Model probability:
{prob:.2f}

Patient profile:
{user_profile}

Food or meal:
{food_item}

Dietary guidelines:
{GUIDELINES}

Task:

Give a concise, context-aware dietary assessment of this
food or meal.

Consider:

- carbohydrate quality
- glycemic impact
- portion size
- fiber
- protein
- added sugar
- fat quantity
- dietary preference
- allergies
- overall meal composition

Explain briefly why the baseline ML result should not
automatically be interpreted as a judgment about the
individual food.

Keep the response below 150 words.

Finish with ONE practical recommendation.

Do not diagnose, treat, cure, or prevent a medical condition.
Do not tell the patient to change medication.
"""

    fallback_models = [
        "gemini-flash-latest",
        "gemini-2.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-flash-lite-latest",
    ]

    for selected_model in fallback_models:
        try:
            response = client.models.generate_content(
                model=selected_model,
                contents=prompt,
            )

            if response.text:
                return response.text

        except Exception:
            continue

    return "AI correction is temporarily unavailable. Please try again later."


# ============================================================
# PDF REPORT
# ============================================================

def clean_text(text):
    return (
        str(text)
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def generate_pdf(patient, food_item, baseline_text, ai_text):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_text_color(6, 78, 59)
    pdf.set_font("Arial", style="B", size=18)
    pdf.cell(
        200,
        12,
        txt="Personalized Diabetic Diet Report",
        ln=True,
        align="C",
    )

    pdf.ln(8)

    pdf.set_text_color(6, 95, 70)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 8, "Patient Information", ln=True)

    pdf.set_text_color(30, 41, 59)
    pdf.set_font("Arial", size=10)

    profile_text = (
        f"Name: {patient['name']}\n"
        f"Age: {patient['age']}\n"
        f"Diabetes Type: {patient['diabetes_type']}\n"
        f"Glucose: {patient['glucose']} mg/dL\n"
        f"BMI: {patient['bmi']}\n"
        f"Blood Pressure: {patient['blood_pressure']}\n"
        f"Dietary Preference: {patient['dietary_preference']}\n"
        f"Allergies: {patient['allergies']}\n"
        f"Activity Level: {patient['activity_level']}"
    )

    pdf.multi_cell(0, 7, clean_text(profile_text))
    pdf.ln(6)

    pdf.set_text_color(6, 95, 70)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 8, "Food / Meal", ln=True)

    pdf.set_text_color(30, 41, 59)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 7, clean_text(food_item))
    pdf.ln(6)

    pdf.set_text_color(6, 95, 70)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 8, "Baseline ML Result", ln=True)

    pdf.set_text_color(30, 41, 59)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 7, clean_text(baseline_text))
    pdf.ln(6)

    pdf.set_text_color(6, 95, 70)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 8, "AI-Corrected Dietary Assessment", ln=True)

    pdf.set_text_color(30, 41, 59)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 7, clean_text(ai_text))
    pdf.ln(10)

    pdf.set_text_color(100, 116, 139)
    pdf.set_font("Arial", size=8)
    pdf.multi_cell(
        0,
        5,
        clean_text(
            "Disclaimer: This report is for educational purposes "
            "only and does not constitute medical advice, diagnosis "
            "or treatment. Consult a qualified healthcare "
            "professional for medical guidance."
        ),
    )

    path = "diet_report.pdf"
    pdf.output(path)

    return path


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
<style>
.stApp {
    background:
        radial-gradient(circle at 5% 5%, rgba(16,185,129,0.12), transparent 25%),
        radial-gradient(circle at 95% 10%, rgba(20,184,166,0.10), transparent 25%),
        linear-gradient(135deg, #F0FDF9 0%, #ECFDF5 45%, #F0FDFA 100%);
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1 {
    color: #064E3B !important;
    font-weight: 800 !important;
}

h2 {
    color: #065F46 !important;
    font-weight: 750 !important;
}

h3 {
    color: #047857 !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #022C22 0%, #064E3B 45%, #047857 100%);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.sidebar-subtitle {
    color: #A7F3D0 !important;
    font-size: 13px;
    line-height: 1.6;
}

.sidebar-section {
    color: #6EE7B7 !important;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 20px;
}

.sidebar-info {
    background: rgba(255,255,255,0.09);
    border: 1px solid rgba(255,255,255,0.13);
    border-radius: 12px;
    padding: 13px;
    margin: 8px 0;
    line-height: 1.6;
}

div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    background: #FFFFFF !important;
    color: #064E3B !important;
    border: 1px solid #B7DED0 !important;
    border-radius: 12px !important;
}

label {
    color: #064E3B !important;
    font-weight: 650 !important;
}

div.stButton > button,
button[kind="primaryFormSubmit"] {
    width: 100%;
    background: linear-gradient(135deg, #047857, #059669, #14B8A6) !important;
    color: white !important;
    border: none !important;
    border-radius: 13px !important;
    min-height: 50px;
    font-size: 16px !important;
    font-weight: 750 !important;
}

div[data-testid="stDownloadButton"] button {
    width: 100% !important;
    background: linear-gradient(135deg, #334155, #475569) !important;
    color: white !important;
    border: none !important;
    border-radius: 13px !important;
    min-height: 50px !important;
    font-weight: 700 !important;
}

.nutrition-card {
    width: 100%;
    background: linear-gradient(135deg, #047857 0%, #059669 50%, #0D9488 100%);
    color: white;
    padding: 25px;
    border-radius: 18px;
    margin-top: 12px;
    margin-bottom: 24px;
    box-sizing: border-box;
}

.nutrition-card-title {
    color: white !important;
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 15px;
}

.nutrition-card-body {
    color: white !important;
    font-size: 16px;
    line-height: 1.75;
    overflow-wrap: break-word;
}

.history-card,
.login-card {
    background: white;
    border: 1px solid #D1FAE5;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 14px;
    box-shadow: 0 8px 25px rgba(6,78,59,0.08);
}

.login-card {
    max-width: 600px;
    margin: 50px auto 25px auto;
    padding: 36px;
    background: linear-gradient(145deg, #FFFFFF, #F0FDFA);
    border-radius: 26px;
    text-align: center;
}

.login-icon {
    font-size: 58px;
    margin-bottom: 8px;
}

.login-title {
    color: #064E3B;
    font-size: 30px;
    font-weight: 800;
}

.login-subtitle {
    color: #64748B;
    font-size: 15px;
    line-height: 1.6;
    margin-top: 8px;
}

.profile-card {
    background: linear-gradient(135deg, #064E3B, #047857, #0D9488);
    color: white;
    padding: 28px;
    border-radius: 20px;
    margin-bottom: 25px;
}

.profile-card h2 {
    color: white !important;
}

.profile-card p {
    color: #D1FAE5 !important;
}

.history-food {
    color: #047857;
    font-size: 18px;
    font-weight: 750;
    margin-bottom: 8px;
}

.history-date {
    color: #64748B;
    font-size: 12px;
    margin-bottom: 10px;
}

.history-result {
    color: #334155;
    font-size: 14px;
    line-height: 1.6;
}

.footer-text {
    text-align: center;
    color: #64748B;
    font-size: 12px;
    padding-top: 20px;
}

#MainMenu, footer {
    visibility: hidden;
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = None


# ============================================================
# LOGIN / CREATE ACCOUNT
# ============================================================

if not st.session_state.authenticated:

    st.markdown(
        """
        <div class="login-card">
            <div class="login-icon">🩺</div>
            <div class="login-title">Diabetic Diet Advisory</div>
            <div class="login-subtitle">
                AI + Machine Learning Nutrition Assistant<br>
                Create an account or sign in to access your
                personalized dietary advisory dashboard.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, signup_tab = st.tabs(
        ["🔐 Sign In", "🆕 Create Account"]
    )

    # --------------------------------------------------------
    # SIGN IN
    # --------------------------------------------------------

    with login_tab:
        with st.form("login_form"):
            username = st.text_input(
                "👤 Username",
                placeholder="Enter your username",
            )

            password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Enter your password",
            )

            login_button = st.form_submit_button(
                "🔐 Sign In",
                use_container_width=True,
            )

            if login_button:
                username = username.strip()

                if not username or not password:
                    st.warning(
                        "⚠️ Please enter both username and password."
                    )

                elif authenticate_user(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()

                else:
                    st.error(
                        "❌ Incorrect username or password."
                    )

    # --------------------------------------------------------
    # CREATE ACCOUNT
    # --------------------------------------------------------

    with signup_tab:
        st.info(
            "Create a unique username and password. "
            "Your patient profile will be stored with your account."
        )

        with st.form("create_account_form"):
            st.markdown("### 🔐 Account Details")

            new_username = st.text_input(
                "Choose a unique username",
                placeholder="e.g. anushka123",
            )

            new_password = st.text_input(
                "Create password",
                type="password",
                placeholder="Create a password",
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                placeholder="Re-enter your password",
            )

            st.markdown("### 👤 Personal Information")

            name = st.text_input(
                "Full Name",
                placeholder="Enter your name",
            )

            age = st.number_input(
                "Age",
                min_value=1,
                max_value=120,
                value=30,
            )

            diabetes_type = st.selectbox(
                "Diabetes status",
                [
                    "Not diagnosed / Prefer not to say",
                    "Type 1 diabetes",
                    "Type 2 diabetes",
                    "Prediabetes",
                    "Gestational diabetes",
                    "Other",
                ],
            )

            st.markdown("### 🩸 Health Measurements")

            glucose = st.number_input(
                "Current glucose level (mg/dL)",
                min_value=40.0,
                max_value=500.0,
                value=140.0,
                step=1.0,
            )

            bmi = st.number_input(
                "BMI",
                min_value=10.0,
                max_value=70.0,
                value=25.0,
                step=0.1,
            )

            blood_pressure = st.number_input(
                "Systolic blood pressure (mmHg)",
                min_value=60.0,
                max_value=250.0,
                value=120.0,
                step=1.0,
            )

            st.markdown("### 🥗 Dietary Information")

            dietary_preference = st.selectbox(
                "Dietary preference",
                [
                    "No specific preference",
                    "Vegetarian",
                    "Vegan",
                    "Eggetarian",
                    "Non-vegetarian",
                ],
            )

            allergies = st.text_input(
                "Food allergies / intolerances",
                placeholder="e.g. peanuts, lactose, none",
            )

            activity_level = st.selectbox(
                "Typical activity level",
                [
                    "Mostly sedentary",
                    "Lightly active",
                    "Moderately active",
                    "Very active",
                ],
            )

            create_account_button = st.form_submit_button(
                "✅ Create Account",
                use_container_width=True,
            )

            if create_account_button:
                clean_username = new_username.strip()
                clean_name = name.strip()
                clean_allergies = allergies.strip() or "None"

                if not clean_username:
                    st.error("Please choose a username.")

                elif len(clean_username) < 3:
                    st.error(
                        "Username must contain at least 3 characters."
                    )

                elif " " in clean_username:
                    st.error(
                        "Username cannot contain spaces."
                    )

                elif not new_password:
                    st.error("Please create a password.")

                elif len(new_password) < 6:
                    st.error(
                        "Password must contain at least 6 characters."
                    )

                elif new_password != confirm_password:
                    st.error(
                        "Passwords do not match."
                    )

                elif not clean_name:
                    st.error(
                        "Please enter your full name."
                    )

                elif username_exists(clean_username):
                    st.error(
                        "❌ That username is already registered. "
                        "Please choose another username."
                    )

                else:
                    success, error_message = create_user(
                        clean_username,
                        new_password,
                        clean_name,
                        age,
                        diabetes_type,
                        glucose,
                        bmi,
                        blood_pressure,
                        dietary_preference,
                        clean_allergies,
                        activity_level,
                    )

                    if success:
                        st.session_state.authenticated = True
                        st.session_state.username = clean_username

                        st.success(
                            "🎉 Account created successfully! "
                            "Opening your dashboard..."
                        )

                        st.rerun()

                    else:
                        st.error(
                            f"Could not create account: {error_message}"
                        )

    st.markdown(
        """
        <p style="
            text-align:center;
            color:#047857;
            font-size:13px;
        ">
        🔐 Your password is stored as a secure salted hash.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.stop()


# ============================================================
# CURRENT USER
# ============================================================

current_username = st.session_state.username
patient_data = get_patient(current_username)

# This is mainly a safety fallback for an incomplete database record.
if patient_data is None:
    st.error(
        "Your account exists, but your patient profile could not be found."
    )

    if st.button("Log out"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

    st.stop()


# ============================================================
# CONVERT DATABASE DATA TO DICTIONARY
# ============================================================

patient = {
    "username": patient_data[0],
    "name": patient_data[1],
    "age": patient_data[2],
    "diabetes_type": patient_data[3],
    "glucose": patient_data[4],
    "bmi": patient_data[5],
    "blood_pressure": patient_data[6],
    "dietary_preference": patient_data[7],
    "allergies": patient_data[8],
    "activity_level": patient_data[9],
    "created_at": patient_data[10],
}


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🩺 Diabetic Diet Advisory")

    st.markdown(
        '<p class="sidebar-subtitle">'
        "AI + Machine Learning Nutrition Assistant"
        "</p>",
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        f"""
        <div class="sidebar-info">
        👤 <b>Logged in as</b><br>
        {html.escape(patient["name"])}
        <br><small>@{html.escape(patient["username"])}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

    st.divider()

    st.markdown(
        '<p class="sidebar-section">HOW IT WORKS</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-info">
        🤖 <b>Step 1</b><br>
        ML model analyzes health inputs.
        </div>

        <div class="sidebar-info">
        🍽️ <b>Step 2</b><br>
        Enter your food or meal.
        </div>

        <div class="sidebar-info">
        🧠 <b>Step 3</b><br>
        AI adds dietary context.
        </div>

        <div class="sidebar-info">
        📊 <b>Step 4</b><br>
        Receive a personalized assessment.
        </div>

        <div class="sidebar-info">
        🗂️ <b>Step 5</b><br>
        Your meal history is saved.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        '<p class="sidebar-section">YOUR PROFILE</p>',
        unsafe_allow_html=True,
    )

    sidebar_profile_html = textwrap.dedent(
        f"""
        <div class="sidebar-info">
            🎂 Age: {patient["age"]}<br>
            🩸 Glucose: {patient["glucose"]} mg/dL<br>
            ⚖️ BMI: {patient["bmi"]}<br>
            ❤️ BP: {patient["blood_pressure"]} mmHg
        </div>
        """
    )

    st.markdown(
        sidebar_profile_html,
        unsafe_allow_html=True,
    )


# ============================================================
# DASHBOARD HEADER
# ============================================================

st.markdown(
    f"""
    <div class="profile-card">
        <h2>👋 Hello, {html.escape(patient["name"])}!</h2>
        <p>
            Welcome to your personalized diabetic diet dashboard.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DASHBOARD TABS
# ============================================================

dashboard_tab, history_tab, profile_tab = st.tabs(
    [
        "🍽️ Analyze Meal",
        "🗂️ Meal History",
        "👤 My Profile",
    ]
)


# ============================================================
# ANALYZE MEAL TAB
# ============================================================

with dashboard_tab:
    st.subheader("🍽️ Analyze Your Food")

    st.write(
        "Enter the food or complete meal you want to evaluate."
    )

    st.info(
        "💡 Tip: Enter the complete meal when possible. "
        "For example: **2 bajra rotis with dal, vegetables "
        "and 1 tsp ghee**."
    )

    food_item = st.text_input(
        "🥗 Food item / meal",
        placeholder="e.g. Curd rice with vegetables",
    )

    analyze_button = st.button(
        "🔍 Analyze Food",
        use_container_width=True,
    )

    if analyze_button:
        if not food_item.strip():
            st.warning(
                "🥗 Please enter a food item or meal."
            )

        else:
            with st.spinner(
                "🤖 Running machine-learning model..."
            ):
                pred, prob = baseline_predict(
                    patient["glucose"],
                    patient["bmi"],
                    patient["age"],
                    patient["blood_pressure"],
                )

                baseline_text = (
                    f"{'Higher-risk model signal' if pred == 1 else 'Lower-risk model signal'} "
                    f"(model probability: {prob:.0%})"
                )

            st.subheader("📊 Baseline ML Model")

            if pred == 1:
                st.warning(
                    f"⚠️ **Higher-risk model signal**\n\n"
                    f"Model probability: **{prob:.0%}**"
                )
            else:
                st.success(
                    f"✅ **Lower-risk model signal**\n\n"
                    f"Model probability: **{prob:.0%}**"
                )

            st.subheader("🍴 Food Selected")
            st.info(food_item)

            user_profile = (
                f"Name: {patient['name']}, "
                f"Age: {patient['age']}, "
                f"Diabetes status: {patient['diabetes_type']}, "
                f"Glucose: {patient['glucose']} mg/dL, "
                f"BMI: {patient['bmi']}, "
                f"Systolic BP: {patient['blood_pressure']} mmHg, "
                f"Diet: {patient['dietary_preference']}, "
                f"Allergies: {patient['allergies']}, "
                f"Activity: {patient['activity_level']}"
            )

            with st.spinner(
                "🧠 AI is generating a context-aware nutrition insight..."
            ):
                ai_text = ai_correct(
                    food_item,
                    pred,
                    prob,
                    user_profile,
                )

            st.subheader("🧠 AI-Corrected Dietary Assessment")

            safe_ai_text = html.escape(ai_text).replace(
                "\n",
                "<br>",
            )

            nutrition_card = (
                '<div class="nutrition-card">'
                '<div class="nutrition-card-title">'
                "✨ Context-Aware Nutrition Insight"
                "</div>"
                '<div class="nutrition-card-body">'
                + safe_ai_text
                + "</div>"
                "</div>"
            )

            st.markdown(
                nutrition_card,
                unsafe_allow_html=True,
            )

            save_meal_history(
                current_username,
                food_item.strip(),
                patient["glucose"],
                patient["bmi"],
                patient["blood_pressure"],
                baseline_text,
                prob,
                ai_text,
            )

            st.success(
                "🗂️ This meal has been saved to your personal history."
            )

            st.subheader("📄 Personalized Report")

            try:
                pdf_path = generate_pdf(
                    patient,
                    food_item,
                    baseline_text,
                    ai_text,
                )

                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        "📥 Download PDF Report",
                        data=pdf_file,
                        file_name="diet_report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
            except Exception as error:
                st.error(
                    f"Could not generate the PDF report: {error}"
                )


# ============================================================
# MEAL HISTORY TAB
# ============================================================

with history_tab:
    st.subheader("🗂️ Your Meal History")

    history = get_meal_history(current_username)

    if not history:
        st.info(
            "🍽️ No meals have been analyzed yet. "
            "Your future meal assessments will appear here."
        )

    else:
        st.write(
            f"You have analyzed **{len(history)} meal(s)**."
        )

        for record in history:
            (
                meal_id,
                food_item_history,
                glucose_history,
                bmi_history,
                bp_history,
                baseline_history,
                probability_history,
                ai_history,
                created_at,
            ) = record

            history_html = textwrap.dedent(
                f"""
                <div class="history-card">
                    <div class="history-food">
                        🍽️ {html.escape(str(food_item_history))}
                    </div>

                    <div class="history-date">
                        🕒 {html.escape(str(created_at))}
                    </div>

                    <div class="history-result">
                        🩸 Glucose: {glucose_history} mg/dL
                        &nbsp; | &nbsp;
                        ⚖️ BMI: {bmi_history}
                        &nbsp; | &nbsp;
                        ❤️ BP: {bp_history} mmHg
                        <br><br>
                        📊 {html.escape(str(baseline_history))}
                    </div>
                </div>
                """
            )

            st.markdown(
                history_html,
                unsafe_allow_html=True,
            )

            with st.expander("🧠 View AI assessment"):
                st.write(ai_history)

            st.divider()


# ============================================================
# PROFILE TAB
# ============================================================

with profile_tab:
    st.subheader("👤 My Profile")

    st.info(
        "You can update your patient information at any time. "
        "Your username cannot be changed because it identifies your account."
    )

    edit_profile = st.toggle(
        "✏️ Edit profile",
        value=False,
        key="edit_profile_toggle",
    )

    if edit_profile:
        # Convert stored values to the option lists safely.
        diabetes_options = [
            "Not diagnosed / Prefer not to say",
            "Type 1 diabetes",
            "Type 2 diabetes",
            "Prediabetes",
            "Gestational diabetes",
            "Other",
        ]

        diet_options = [
            "No specific preference",
            "Vegetarian",
            "Vegan",
            "Eggetarian",
            "Non-vegetarian",
        ]

        activity_options = [
            "Mostly sedentary",
            "Lightly active",
            "Moderately active",
            "Very active",
        ]

        current_diabetes = (
            patient["diabetes_type"]
            if patient["diabetes_type"] in diabetes_options
            else "Other"
        )

        current_diet = (
            patient["dietary_preference"]
            if patient["dietary_preference"] in diet_options
            else "No specific preference"
        )

        current_activity = (
            patient["activity_level"]
            if patient["activity_level"] in activity_options
            else "Mostly sedentary"
        )

        with st.form("edit_profile_form"):
            st.markdown("### ✏️ Update Personal Information")

            edit_name = st.text_input(
                "Full Name",
                value=str(patient["name"] or ""),
            )

            edit_age = st.number_input(
                "Age",
                min_value=1,
                max_value=120,
                value=int(patient["age"] or 30),
            )

            edit_diabetes_type = st.selectbox(
                "Diabetes status",
                diabetes_options,
                index=diabetes_options.index(current_diabetes),
            )

            st.markdown("### 🩸 Update Health Measurements")

            edit_glucose = st.number_input(
                "Current glucose level (mg/dL)",
                min_value=40.0,
                max_value=500.0,
                value=float(patient["glucose"] or 140.0),
                step=1.0,
            )

            edit_bmi = st.number_input(
                "BMI",
                min_value=10.0,
                max_value=70.0,
                value=float(patient["bmi"] or 25.0),
                step=0.1,
            )

            edit_bp = st.number_input(
                "Systolic blood pressure (mmHg)",
                min_value=60.0,
                max_value=250.0,
                value=float(patient["blood_pressure"] or 120.0),
                step=1.0,
            )

            st.markdown("### 🥗 Update Dietary Information")

            edit_diet = st.selectbox(
                "Dietary preference",
                diet_options,
                index=diet_options.index(current_diet),
            )

            edit_allergies = st.text_input(
                "Food allergies / intolerances",
                value=str(patient["allergies"] or "None"),
            )

            edit_activity = st.selectbox(
                "Typical activity level",
                activity_options,
                index=activity_options.index(current_activity),
            )

            save_profile_button = st.form_submit_button(
                "💾 Save Profile Changes",
                use_container_width=True,
            )

            if save_profile_button:
                clean_name = edit_name.strip()
                clean_allergies = edit_allergies.strip() or "None"

                if not clean_name:
                    st.error("Please enter your full name.")
                else:
                    updated = update_patient_profile(
                        current_username,
                        clean_name,
                        edit_age,
                        edit_diabetes_type,
                        edit_glucose,
                        edit_bmi,
                        edit_bp,
                        edit_diet,
                        clean_allergies,
                        edit_activity,
                    )

                    if updated:
                        st.session_state.profile_saved = True
                        st.rerun()
                    else:
                        st.error(
                            "Could not update your profile. "
                            "Please try again."
                        )

    if st.session_state.pop("profile_saved", False):
        st.success("✅ Your profile has been updated successfully.")

    # Reload the latest values after a possible update.
    latest_patient_data = get_patient(current_username)

    if latest_patient_data:
        latest_patient = {
            "username": latest_patient_data[0],
            "name": latest_patient_data[1],
            "age": latest_patient_data[2],
            "diabetes_type": latest_patient_data[3],
            "glucose": latest_patient_data[4],
            "bmi": latest_patient_data[5],
            "blood_pressure": latest_patient_data[6],
            "dietary_preference": latest_patient_data[7],
            "allergies": latest_patient_data[8],
            "activity_level": latest_patient_data[9],
            "created_at": latest_patient_data[10],
        }

        profile_html = textwrap.dedent(
            f"""
            <div class="history-card">
                <div class="history-food">
                    👤 {html.escape(str(latest_patient["name"]))}
                </div>

                <div class="history-result">
                    🔐 Username:
                    {html.escape(str(latest_patient["username"]))}<br>
                    🎂 Age: {latest_patient["age"]}<br>
                    🩺 Diabetes status:
                    {html.escape(str(latest_patient["diabetes_type"]))}<br>
                    🩸 Glucose:
                    {latest_patient["glucose"]} mg/dL<br>
                    ⚖️ BMI: {latest_patient["bmi"]}<br>
                    ❤️ Blood Pressure:
                    {latest_patient["blood_pressure"]} mmHg<br>
                    🥗 Dietary preference:
                    {html.escape(str(latest_patient["dietary_preference"]))}<br>
                    🚫 Allergies:
                    {html.escape(str(latest_patient["allergies"]))}<br>
                    🏃 Activity level:
                    {html.escape(str(latest_patient["activity_level"]))}<br>
                    📅 Account created:
                    {html.escape(str(latest_patient["created_at"]))}
                </div>
            </div>
            """
        )

        st.markdown(
            profile_html,
            unsafe_allow_html=True,
        )


# ============================================================
# DISCLAIMER
# ============================================================

st.markdown("---")

st.caption(
    "⚠️ Medical Disclaimer: This application is an educational "
    "AI/ML project. It does not diagnose, treat, cure or prevent "
    "diabetes and should not replace advice from a qualified "
    "healthcare professional."
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer-text">
    🩺 <b>Diabetic Diet Advisory</b>
    &nbsp; • &nbsp;
    Python + Streamlit + Machine Learning + Generative AI
    </div>
    """,
    unsafe_allow_html=True,
)
