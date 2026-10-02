import streamlit as st
import pickle
import numpy as np
from fpdf import FPDF
from google import genai

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Diabetic Diet Advisory",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# PROFESSIONAL COLOR PALETTE
# ============================================================

PRIMARY = "#0B6E4F"
PRIMARY_LIGHT = "#18A879"
DARK = "#063B2D"
TEAL = "#00A896"
BLUE = "#3B82F6"
PURPLE = "#7C3AED"
RED = "#EF4444"
ORANGE = "#F59E0B"
WHITE = "#FFFFFF"
TEXT = "#1F2937"
MUTED = "#6B7280"
BG = "#F3F8F6"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    f"""
<style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    .stApp {{
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(24,168,121,0.10),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(59,130,246,0.08),
                transparent 28%
            ),
            linear-gradient(
                135deg,
                #F4FAF7 0%,
                #EEF8F5 45%,
                #F7FAFC 100%
            );

        color: {TEXT};
    }}

    .block-container {{
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }}

    /* Remove default Streamlit decoration */

    #MainMenu {{
        visibility: hidden;
    }}

    footer {{
        visibility: hidden;
    }}

    header {{
        background: transparent !important;
    }}

    /* ======================================================
       HERO HEADER
       ====================================================== */

    .hero {{
        position: relative;
        overflow: hidden;

        padding: 42px 45px;

        border-radius: 30px;

        background:
            radial-gradient(
                circle at 85% 15%,
                rgba(255,255,255,0.20),
                transparent 25%
            ),
            linear-gradient(
                135deg,
                #063B2D 0%,
                #087F5B 45%,
                #12A875 100%
            );

        box-shadow:
            0 20px 50px rgba(6,59,45,0.22);

        color: white;

        margin-bottom: 30px;
    }}

    .hero::before {{
        content: "";

        position: absolute;

        width: 250px;
        height: 250px;

        border-radius: 50%;

        background: rgba(255,255,255,0.07);

        right: -80px;
        top: -100px;
    }}

    .hero::after {{
        content: "";

        position: absolute;

        width: 180px;
        height: 180px;

        border-radius: 50%;

        background: rgba(255,255,255,0.05);

        right: 180px;
        bottom: -100px;
    }}

    .hero-content {{
        position: relative;
        z-index: 2;
    }}

    .hero-badge {{
        display: inline-block;

        background: rgba(255,255,255,0.15);

        border: 1px solid rgba(255,255,255,0.25);

        padding: 7px 15px;

        border-radius: 50px;

        font-size: 13px;

        font-weight: 600;

        margin-bottom: 15px;

        backdrop-filter: blur(10px);
    }}

    .hero-title {{
        font-size: 46px;

        font-weight: 800;

        letter-spacing: -1.5px;

        margin: 0;

        line-height: 1.1;
    }}

    .hero-subtitle {{
        font-size: 17px;

        color: rgba(255,255,255,0.88);

        margin-top: 14px;

        max-width: 750px;

        line-height: 1.6;
    }}

    /* ======================================================
       SECTION HEADINGS
       ====================================================== */

    .section-heading {{
        display: flex;
        align-items: center;
        gap: 12px;

        margin-top: 28px;
        margin-bottom: 18px;

        font-size: 23px;

        font-weight: 800;

        color: {DARK};
    }}

    .section-icon {{
        width: 40px;
        height: 40px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 12px;

        background: linear-gradient(
            135deg,
            #087F5B,
            #18A879
        );

        color: white;

        box-shadow: 0 6px 15px rgba(8,127,91,0.20);
    }}

    /* ======================================================
       GLASS CARDS
       ====================================================== */

    .glass-card {{
        background: rgba(255,255,255,0.80);

        border: 1px solid rgba(255,255,255,0.9);

        border-radius: 22px;

        padding: 25px;

        box-shadow:
            0 10px 30px rgba(31,41,55,0.07);

        backdrop-filter: blur(15px);

        margin-bottom: 20px;
    }}

    /* ======================================================
       METRIC CARDS
       ====================================================== */

    .metric {{
        position: relative;

        overflow: hidden;

        background: white;

        border-radius: 20px;

        padding: 22px;

        min-height: 135px;

        border: 1px solid #E5EEE9;

        box-shadow:
            0 8px 25px rgba(31,41,55,0.06);

        transition: all 0.25s ease;
    }}

    .metric:hover {{
        transform: translateY(-4px);

        box-shadow:
            0 15px 35px rgba(31,41,55,0.10);
    }}

    .metric::after {{
        content: "";

        position: absolute;

        width: 90px;
        height: 90px;

        border-radius: 50%;

        right: -35px;
        top: -35px;

        background: rgba(18,168,117,0.07);
    }}

    .metric-icon {{
        font-size: 26px;
        margin-bottom: 7px;
    }}

    .metric-label {{
        color: {MUTED};

        font-size: 13px;

        font-weight: 600;

        text-transform: uppercase;

        letter-spacing: 0.5px;
    }}

    .metric-value {{
        font-size: 27px;

        font-weight: 800;

        color: {DARK};

        margin-top: 4px;
    }}

    /* ======================================================
       FOOD INPUT CARD
       ====================================================== */

    .food-banner {{
        background:
            linear-gradient(
                135deg,
                rgba(255,250,235,0.95),
                rgba(255,244,211,0.95)
            );

        border: 1px solid #F4E5B1;

        border-radius: 20px;

        padding: 20px 24px;

        margin-bottom: 12px;
    }}

    .food-banner-title {{
        color: #8A5A00;

        font-size: 15px;

        font-weight: 700;
    }}

    .food-banner-text {{
        color: #856404;

        margin-top: 5px;

        font-size: 14px;
    }}

    /* ======================================================
       RESULT CARDS
       ====================================================== */

    .result-high {{
        background:
            linear-gradient(
                135deg,
                #FFF5F5 0%,
                #FFE4E4 100%
            );

        border: 1px solid #FECACA;

        border-left: 6px solid {RED};

        border-radius: 22px;

        padding: 27px;

        box-shadow:
            0 10px 30px rgba(239,68,68,0.08);
    }}

    .result-low {{
        background:
            linear-gradient(
                135deg,
                #F0FFF8 0%,
                #DDF9EC 100%
            );

        border: 1px solid #BBEBD3;

        border-left: 6px solid {PRIMARY_LIGHT};

        border-radius: 22px;

        padding: 27px;

        box-shadow:
            0 10px 30px rgba(18,168,117,0.08);
    }}

    .result-label {{
        font-size: 14px;

        font-weight: 700;

        text-transform: uppercase;

        letter-spacing: 0.7px;

        color: #6B7280;
    }}

    .result-title {{
        font-size: 26px;

        font-weight: 800;

        margin-top: 6px;
    }}

    .result-probability {{
        font-size: 52px;

        font-weight: 900;

        line-height: 1;

        margin: 12px 0;
    }}

    .result-description {{
        color: #4B5563;

        font-size: 14px;

        line-height: 1.6;
    }}

    /* ======================================================
       AI CARD
       ====================================================== */

    .ai-card {{
        position: relative;

        overflow: hidden;

        background:
            linear-gradient(
                135deg,
                #F8F5FF 0%,
                #EEE8FF 50%,
                #F6F3FF 100%
            );

        border: 1px solid #DDD2FF;

        border-radius: 24px;

        padding: 30px;

        box-shadow:
            0 15px 40px rgba(124,58,237,0.10);
    }}

    .ai-card::before {{
        content: "";

        position: absolute;

        width: 180px;
        height: 180px;

        border-radius: 50%;

        background: rgba(124,58,237,0.06);

        right: -60px;
        top: -70px;
    }}

    .ai-badge {{
        display: inline-block;

        background: linear-gradient(
            135deg,
            #6D28D9,
            #8B5CF6
        );

        color: white;

        padding: 7px 14px;

        border-radius: 50px;

        font-size: 12px;

        font-weight: 700;

        margin-bottom: 14px;

        box-shadow:
            0 5px 12px rgba(109,40,217,0.20);
    }}

    .ai-title {{
        font-size: 25px;

        font-weight: 800;

        color: #4C1D95;

        margin-bottom: 12px;
    }}

    .ai-text {{
        color: #374151;

        font-size: 16px;

        line-height: 1.75;

        position: relative;

        z-index: 2;
    }}

    /* ======================================================
       INFORMATION CARD
       ====================================================== */

    .info-box {{
        background:
            linear-gradient(
                135deg,
                #EFF8FF,
                #E7F5FF
            );

        border: 1px solid #BFDBFE;

        border-radius: 20px;

        padding: 23px;

        border-left: 5px solid {BLUE};
    }}

    .info-title {{
        font-size: 18px;

        font-weight: 800;

        color: #1E40AF;

        margin-bottom: 7px;
    }}

    .info-text {{
        color: #374151;

        line-height: 1.65;

        font-size: 14px;
    }}

    /* ======================================================
       SIDEBAR
       ====================================================== */

    [data-testid="stSidebar"] {{
        background:
            linear-gradient(
                180deg,
                #063B2D 0%,
                #07543F 55%,
                #063B2D 100%
            );
    }}

    [data-testid="stSidebar"] * {{
        color: white !important;
    }}

    .sidebar-logo {{
        text-align: center;

        padding: 15px 5px 25px 5px;
    }}

    .sidebar-logo-icon {{
        font-size: 45px;
    }}

    .sidebar-logo-title {{
        font-size: 22px;

        font-weight: 800;

        margin-top: 5px;
    }}

    .sidebar-logo-subtitle {{
        color: rgba(255,255,255,0.7) !important;

        font-size: 12px;
    }}

    .sidebar-item {{
        background: rgba(255,255,255,0.08);

        border: 1px solid rgba(255,255,255,0.08);

        padding: 14px;

        border-radius: 14px;

        margin: 8px 0;

        font-size: 13px;
    }}

    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton > button {{
        background:
            linear-gradient(
                135deg,
                #087F5B,
                #12A875
            ) !important;

        color: white !important;

        border: none !important;

        border-radius: 14px !important;

        padding: 14px 22px !important;

        font-size: 16px !important;

        font-weight: 750 !important;

        min-height: 52px;

        box-shadow:
            0 8px 20px rgba(8,127,91,0.22);

        transition: all 0.2s ease !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px);

        box-shadow:
            0 12px 25px rgba(8,127,91,0.30);
    }}

    .stDownloadButton > button {{
        width: 100%;

        background:
            linear-gradient(
                135deg,
                #334155,
                #475569
            ) !important;

        color: white !important;

        border: none !important;

        border-radius: 14px !important;

        min-height: 50px;

        font-weight: 700 !important;
    }}

    /* ======================================================
       INPUTS
       ====================================================== */

    .stNumberInput input,
    .stTextInput input {{
        border-radius: 12px !important;

        border: 1px solid #D6E5DF !important;

        background: rgba(255,255,255,0.9) !important;

        color: #1F2937 !important;
    }}

    .stNumberInput input:focus,
    .stTextInput input:focus {{
        border-color: #12A875 !important;

        box-shadow:
            0 0 0 2px rgba(18,168,117,0.12) !important;
    }}

    /* ======================================================
       DISCLAIMER
       ====================================================== */

    .disclaimer {{
        background: rgba(255,255,255,0.75);

        border: 1px solid #E5E7EB;

        border-radius: 16px;

        padding: 18px;

        text-align: center;

        color: #6B7280;

        font-size: 12px;

        line-height: 1.6;

        margin-top: 40px;
    }}

    /* ======================================================
       FOOTER
       ====================================================== */

    .footer {{
        text-align: center;

        color: #94A3B8;

        font-size: 12px;

        padding: 25px;
    }}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# LOAD MODEL
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
# GUIDELINES
# ============================================================

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


# ============================================================
# BASELINE PREDICTION
# ============================================================

def baseline_predict(glucose, bmi, age, bp):

    features = np.array([
        [1, glucose, bp, 20, 80, bmi, 0.5, age]
    ])

    scaled = scaler.transform(features)

    pred = model.predict(scaled)[0]

    prob = model.predict_proba(scaled)[0][1]

    return pred, prob


# ============================================================
# AI CORRECTION
# ============================================================

def ai_correct(
    food_item,
    baseline_verdict,
    prob,
    user_profile
):

    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )

    prompt = f"""
You are a nutritionist agent.

A baseline ML model produced this result:

{'HIGH RISK' if baseline_verdict == 1 else 'LOW RISK'}

Model probability: {prob:.2f}

User profile:
{user_profile}

Food being evaluated:
{food_item}

Dietary guidelines:
{GUIDELINES}

Provide a concise, context-aware dietary assessment.

Consider:
- carbohydrate quality
- glycemic impact
- portion size
- fiber
- protein
- added sugar
- fats
- the overall meal context

Explain briefly why the ML signal may not directly describe
whether the particular food is appropriate.

Keep the response below 150 words.

Finish with ONE practical recommendation.

Do not diagnose or treat a medical condition.
"""

    fallback_models = [
        "gemini-flash-latest",
        "gemini-2.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-flash-lite-latest"
    ]

    last_error = None

    for selected_model in fallback_models:

        try:

            response = client.models.generate_content(
                model=selected_model,
                contents=prompt
            )

            return response.text

        except Exception as e:

            last_error = e

    return (
        "AI analysis is temporarily unavailable. "
        "Please try again later."
    )


# ============================================================
# PDF
# ============================================================

def clean_text(text):

    return (
        text
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def generate_pdf(
    user_profile,
    food_item,
    baseline_text,
    ai_text
):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font(
        "Arial",
        style="B",
        size=18
    )

    pdf.cell(
        200,
        12,
        txt="Personalized Diabetic Diet Report",
        ln=True,
        align="C"
    )

    pdf.set_font(
        "Arial",
        size=11
    )

    pdf.ln(10)

    pdf.multi_cell(
        0,
        8,
        clean_text(
            f"User Profile: {user_profile}"
        )
    )

    pdf.multi_cell(
        0,
        8,
        clean_text(
            f"Food Item: {food_item}"
        )
    )

    pdf.ln(5)

    pdf.multi_cell(
        0,
        8,
        clean_text(
            f"Baseline Model Verdict: {baseline_text}"
        )
    )

    pdf.ln(5)

    pdf.multi_cell(
        0,
        8,
        clean_text(
            f"AI-Corrected Dietary Assessment:\n{ai_text}"
        )
    )

    pdf.ln(12)

    pdf.set_font(
        "Arial",
        size=9
    )

    pdf.multi_cell(
        0,
        6,
        clean_text(
            "Disclaimer: This report is for educational purposes "
            "only and does not replace professional medical advice."
        )
    )

    path = "diet_report.pdf"

    pdf.output(path)

    return path


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-logo">

            <div class="sidebar-logo-icon">
                🩺
            </div>

            <div class="sidebar-logo-title">
                Diet Advisory
            </div>

            <div class="sidebar-logo-subtitle">
                AI + Machine Learning
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("### 🧠 How it works")

    st.markdown(
        """
        <div class="sidebar-item">
        🤖 <b>Step 1</b><br>
        ML model analyzes health inputs.
        </div>

        <div class="sidebar-item">
        🍽️ <b>Step 2</b><br>
        Food or meal is provided.
        </div>

        <div class="sidebar-item">
        🧠 <b>Step 3</b><br>
        AI adds nutritional context.
        </div>

        <div class="sidebar-item">
        📋 <b>Step 4</b><br>
        Personalized assessment is generated.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("### 🌾 Dietary Focus")

    st.markdown(
        """
        <div class="sidebar-item">
        🌾 Whole grains & millets
        </div>

        <div class="sidebar-item">
        🫘 Fiber-rich foods
        </div>

        <div class="sidebar-item">
        🥗 Balanced portions
        </div>

        <div class="sidebar-item">
        🍬 Limited added sugar
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.caption(
        "⚠️ Educational AI/ML project. "
        "Not a medical diagnostic system."
    )


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-content">

            <div class="hero-badge">
                ✨ AI-POWERED NUTRITION ANALYSIS
            </div>

            <div class="hero-title">
                Diabetic Diet Advisory
            </div>

            <div class="hero-subtitle">
                Understand how your health profile and food choices
                interact using machine learning and context-aware
                artificial intelligence.
            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PROFILE SECTION
# ============================================================

st.markdown(
    """
    <div class="section-heading">
        <div class="section-icon">👤</div>
        Health Profile
    </div>
    """,
    unsafe_allow_html=True
)


col1, col2, col3, col4 = st.columns(4)

with col1:

    age = st.number_input(
        "Age",
        min_value=18,
        max_value=90,
        value=45
    )

with col2:

    glucose = st.number_input(
        "Glucose (mg/dL)",
        min_value=70,
        max_value=300,
        value=140
    )

with col3:

    bmi = st.number_input(
        "BMI",
        min_value=15.0,
        max_value=50.0,
        value=25.0,
        step=0.1
    )

with col4:

    bp = st.number_input(
        "Blood Pressure",
        min_value=60,
        max_value=140,
        value=80
    )


# ============================================================
# PROFILE METRICS
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)

metrics = [
    ("🎂", "AGE", str(age)),
    ("🩸", "GLUCOSE", f"{glucose} mg/dL"),
    ("⚖️", "BMI", f"{bmi:.1f}"),
    ("❤️", "BLOOD PRESSURE", f"{bp} mmHg"),
]

for col, (icon, label, value) in zip(
    [m1, m2, m3, m4],
    metrics
):

    with col:

        st.markdown(
            f"""
            <div class="metric">

                <div class="metric-icon">
                    {icon}
                </div>

                <div class="metric-label">
                    {label}
                </div>

                <div class="metric-value">
                    {value}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# FOOD SECTION
# ============================================================

st.markdown(
    """
    <div class="section-heading">
        <div class="section-icon">🍽️</div>
        Food Analysis
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="food-banner">

        <div class="food-banner-title">
            🍴 Enter the food or meal you want to analyze
        </div>

        <div class="food-banner-text">
            Include ingredients and quantities when possible.
            Example: <b>Bajra roti with 1 tsp ghee and 5g jaggery</b>
        </div>

    </div>
    """,
    unsafe_allow_html=True
)

food_item = st.text_input(
    "Food item",
    placeholder="e.g., Bajra roti with ghee and jaggery",
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)

analyze = st.button(
    "🔍  ANALYZE MY FOOD"
)


# ============================================================
# ANALYSIS
# ============================================================

if analyze:

    if not food_item.strip():

        st.warning(
            "Please enter a food item or meal to continue."
        )

    else:

        # ----------------------------------------------------
        # BASELINE ML
        # ----------------------------------------------------

        with st.spinner(
            "🤖 Running machine-learning analysis..."
        ):

            pred, prob = baseline_predict(
                glucose,
                bmi,
                age,
                bp
            )

            baseline_text = (
                f"{'High diabetes risk' if pred == 1 else 'Low diabetes risk'} "
                f"(confidence: {prob:.0%})"
            )


        # ----------------------------------------------------
        # RESULTS
        # ----------------------------------------------------

        st.markdown(
            """
            <div class="section-heading">
                <div class="section-icon">📊</div>
                Analysis Results
            </div>
            """,
            unsafe_allow_html=True
        )


        result_col1, result_col2 = st.columns(
            [1, 1.3],
            gap="large"
        )


        # ----------------------------------------------------
        # ML RESULT
        # ----------------------------------------------------

        with result_col1:

            if pred == 1:

                st.markdown(
                    f"""
                    <div class="result-high">

                        <div class="result-label">
                            Baseline ML Signal
                        </div>

                        <div class="result-title"
                             style="color:#B91C1C;">
                            ⚠️ Higher Risk Signal
                        </div>

                        <div class="result-probability"
                             style="color:#DC2626;">
                            {prob:.0%}
                        </div>

                        <div class="result-description">
                            Model probability for class 1 based on
                            the supplied health inputs.
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"""
                    <div class="result-low">

                        <div class="result-label">
                            Baseline ML Signal
                        </div>

                        <div class="result-title"
                             style="color:#087F5B;">
                            ✅ Lower Risk Signal
                        </div>

                        <div class="result-probability"
                             style="color:#087F5B;">
                            {prob:.0%}
                        </div>

                        <div class="result-description">
                            Model probability for class 1 based on
                            the supplied health inputs.
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


        # ----------------------------------------------------
        # FOOD RESULT
        # ----------------------------------------------------

        with result_col2:

            st.markdown(
                f"""
                <div class="glass-card"
                     style="height:100%;">

                    <div style="
                        color:#6B7280;
                        font-size:13px;
                        font-weight:700;
                        text-transform:uppercase;
                        letter-spacing:0.6px;
                    ">
                        Selected Food / Meal
                    </div>

                    <div style="
                        font-size:25px;
                        font-weight:800;
                        color:#063B2D;
                        margin-top:12px;
                        line-height:1.35;
                    ">
                        🍽️ {food_item}
                    </div>

                    <div style="
                        color:#6B7280;
                        font-size:14px;
                        margin-top:15px;
                    ">
                        The AI layer will evaluate this food in
                        the context of your health profile.
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


        # ----------------------------------------------------
        # AI ANALYSIS
        # ----------------------------------------------------

        user_profile = (
            f"Age {age}, "
            f"Glucose {glucose} mg/dL, "
            f"BMI {bmi}, "
            f"BP {bp}"
        )


        with st.spinner(
            "🧠 Gemini AI is generating a context-aware assessment..."
        ):

            ai_text = ai_correct(
                food_item,
                pred,
                prob,
                user_profile
            )


        st.markdown(
            """
            <div class="section-heading">
                <div class="section-icon">🧠</div>
                AI-Corrected Dietary Assessment
            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            f"""
            <div class="ai-card">

                <div class="ai-badge">
                    ✨ GEMINI AI INSIGHT
                </div>

                <div class="ai-title">
                    Context-Aware Nutrition Assessment
                </div>

                <div class="ai-text">
                    {ai_text}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # WHY AI CORRECTION?
        # ----------------------------------------------------

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="info-box">

                <div class="info-title">
                    💡 Why does the AI correction layer matter?
                </div>

                <div class="info-text">

                    The machine-learning model evaluates patterns
                    from the health measurements provided to it.
                    It does not necessarily understand the nutritional
                    composition of an individual meal.

                    <br><br>

                    The AI layer adds additional context such as
                    carbohydrate quality, fiber, portion size,
                    added sugar, healthy fats, and the overall meal
                    composition.

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # PDF REPORT
        # ----------------------------------------------------

        st.markdown("<br>", unsafe_allow_html=True)

        pdf_path = generate_pdf(
            user_profile,
            food_item,
            baseline_text,
            ai_text
        )

        with open(pdf_path, "rb") as f:

            st.download_button(
                label="📄  DOWNLOAD PERSONALIZED PDF REPORT",
                data=f,
                file_name="diet_report.pdf",
                mime="application/pdf"
            )


# ============================================================
# DISCLAIMER
# ============================================================

st.markdown(
    """
    <div class="disclaimer">

        <b>⚠️ Important Medical Disclaimer</b>

        <br><br>

        This application is an educational AI/ML project.
        It is not intended to diagnose, treat, cure, or prevent
        diabetes or any other medical condition.

        <br>

        The model output and AI-generated dietary assessment should
        not replace advice from a qualified healthcare professional.

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        🩺 <b>Diabetic Diet Advisory</b>

        &nbsp; • &nbsp;

        AI + Machine Learning

        &nbsp; • &nbsp;

        Built with Streamlit

    </div>
    """,
    unsafe_allow_html=True
)
