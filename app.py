import streamlit as st
import pickle
import numpy as np
from fpdf import FPDF
from google import genai
import html


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
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   MAIN APP
   ============================================================ */

.stApp {
    background:
        radial-gradient(
            circle at 5% 5%,
            rgba(16, 185, 129, 0.12),
            transparent 25%
        ),
        radial-gradient(
            circle at 95% 10%,
            rgba(20, 184, 166, 0.10),
            transparent 25%
        ),
        linear-gradient(
            135deg,
            #F0FDF9 0%,
            #ECFDF5 45%,
            #F0FDFA 100%
        );
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* ============================================================
   HEADINGS
   ============================================================ */

h1 {
    color: #064E3B !important;
    font-weight: 800 !important;
    font-size: 42px !important;
    letter-spacing: -1px;
}

h2 {
    color: #065F46 !important;
    font-weight: 750 !important;
}

h3 {
    color: #047857 !important;
    font-weight: 700 !important;
}

p {
    color: #475569;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #022C22 0%,
            #064E3B 45%,
            #047857 100%
        );
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
    background: rgba(255, 255, 255, 0.09);
    border: 1px solid rgba(255, 255, 255, 0.13);
    border-radius: 12px;
    padding: 13px;
    margin: 8px 0;
    line-height: 1.6;
}


/* ============================================================
   DIVIDERS
   ============================================================ */

hr {
    border: none !important;
    height: 1px !important;

    background:
        linear-gradient(
            90deg,
            transparent,
            #86EFAC,
            transparent
        ) !important;
}


/* ============================================================
   INPUT LABELS
   ============================================================ */

label {
    color: #064E3B !important;
    font-weight: 650 !important;
}


/* ============================================================
   NUMBER INPUTS
   ============================================================ */

div[data-testid="stNumberInput"] input {
    background: #FFFFFF !important;
    color: #064E3B !important;

    border: 1px solid #B7DED0 !important;
    border-radius: 12px !important;

    font-weight: 600 !important;
}

div[data-testid="stNumberInput"] input:focus {
    border: 2px solid #10B981 !important;

    box-shadow:
        0 0 0 3px rgba(16, 185, 129, 0.12) !important;
}


/* ============================================================
   TEXT INPUT
   ============================================================ */

div[data-testid="stTextInput"] input {
    background: #FFFFFF !important;
    color: #064E3B !important;

    border: 1px solid #B7DED0 !important;
    border-radius: 12px !important;

    padding: 12px !important;

    font-size: 16px !important;
}

div[data-testid="stTextInput"] input:focus {
    border: 2px solid #10B981 !important;

    box-shadow:
        0 0 0 3px rgba(16, 185, 129, 0.12) !important;
}


/* ============================================================
   ANALYZE BUTTON
   ============================================================ */

div.stButton > button {
    width: 100%;

    background:
        linear-gradient(
            135deg,
            #047857 0%,
            #059669 50%,
            #14B8A6 100%
        ) !important;

    color: #FFFFFF !important;

    border: none !important;

    border-radius: 13px !important;

    min-height: 52px;

    font-size: 17px !important;

    font-weight: 750 !important;

    box-shadow:
        0 8px 20px rgba(5, 150, 105, 0.22);

    transition: all 0.25s ease;
}

div.stButton > button p {
    color: #FFFFFF !important;
}

div.stButton > button span {
    color: #FFFFFF !important;
}

div.stButton > button:hover {
    transform: translateY(-2px);

    box-shadow:
        0 12px 28px rgba(5, 150, 105, 0.30);
}


/* ============================================================
   DOWNLOAD PDF BUTTON
   ============================================================ */

div[data-testid="stDownloadButton"] button {
    width: 100% !important;

    background:
        linear-gradient(
            135deg,
            #334155 0%,
            #475569 100%
        ) !important;

    color: #FFFFFF !important;

    border: none !important;

    border-radius: 13px !important;

    min-height: 52px !important;

    font-size: 16px !important;

    font-weight: 700 !important;

    box-shadow:
        0 7px 18px rgba(51, 65, 85, 0.20);

    transition: all 0.25s ease;
}

div[data-testid="stDownloadButton"] button p {
    color: #FFFFFF !important;
}

div[data-testid="stDownloadButton"] button span {
    color: #FFFFFF !important;
}

div[data-testid="stDownloadButton"] button:hover {
    background:
        linear-gradient(
            135deg,
            #1E293B 0%,
            #334155 100%
        ) !important;

    color: #FFFFFF !important;

    transform: translateY(-2px);
}


/* ============================================================
   AI NUTRITION CARD
   ============================================================ */

.nutrition-card {
    width: 100%;

    background:
        linear-gradient(
            135deg,
            #047857 0%,
            #059669 50%,
            #0D9488 100%
        );

    color: #FFFFFF;

    padding: 24px;

    border-radius: 18px;

    margin-top: 12px;
    margin-bottom: 24px;

    box-shadow:
        0 10px 28px rgba(5, 150, 105, 0.22);

    box-sizing: border-box;

    overflow: visible;
}

.nutrition-card-title {
    color: #FFFFFF !important;

    font-size: 20px;

    font-weight: 800;

    margin-bottom: 16px;

    line-height: 1.4;
}

.nutrition-card-body {
    color: #FFFFFF !important;

    font-size: 16px;

    line-height: 1.75;

    white-space: normal;

    overflow: visible;

    word-wrap: break-word;

    overflow-wrap: break-word;
}

.nutrition-card-body p {
    color: #FFFFFF !important;

    margin-top: 0;

    margin-bottom: 13px;
}

.nutrition-card-recommendation {
    margin-top: 18px;

    padding: 13px 15px;

    background: rgba(255, 255, 255, 0.13);

    border-left: 4px solid #A7F3D0;

    border-radius: 8px;

    color: #FFFFFF !important;
}


/* ============================================================
   INFORMATION BOX
   ============================================================ */

div[data-testid="stAlert"] {
    border-radius: 14px !important;
}


/* ============================================================
   EXPANDER
   ============================================================ */

div[data-testid="stExpander"] {
    border: 1px solid #CDE9DE !important;

    border-radius: 14px !important;

    background: rgba(255, 255, 255, 0.75) !important;
}


/* ============================================================
   FOOTER
   ============================================================ */

.footer-text {
    text-align: center;

    color: #64748B;

    font-size: 12px;

    padding-top: 20px;
}


/* ============================================================
   HIDE STREAMLIT DEFAULT MENU
   ============================================================ */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# LOAD MACHINE LEARNING MODEL
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
Diabetic dietary guidelines (summary):

- Prefer low glycemic index (GI) foods such as millets,
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
"""


# ============================================================
# BASELINE ML PREDICTION
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
# AI CORRECTION LAYER
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
You are a nutritionist agent assisting an educational
diabetic dietary advisory application.

Baseline ML result:
{'HIGH RISK' if baseline_verdict == 1 else 'LOW RISK'}

Model probability:
{prob:.2f}

User profile:
{user_profile}

Food item:
{food_item}

Dietary guidelines:
{GUIDELINES}

Task:

Give a concise, context-aware dietary assessment of this
food item for this user.

Consider:

- carbohydrate quality
- glycemic impact
- portion size
- fiber
- protein
- added sugar
- fat quantity
- overall meal composition

Briefly explain why the baseline ML result should not
automatically be interpreted as a judgment about the
individual food item.

Keep the response below 150 words.

Finish with ONE practical recommendation.

Do not diagnose, treat, cure, or prevent any medical condition.
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

            if response.text:
                return response.text

        except Exception as error:

            last_error = error

    return (
        "AI correction is temporarily unavailable. "
        "Please try again later."
    )


# ============================================================
# PDF TEXT CLEANING
# ============================================================

def clean_text(text):

    return (
        text
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


# ============================================================
# PDF GENERATION
# ============================================================

def generate_pdf(
    user_profile,
    food_item,
    baseline_text,
    ai_text
):

    pdf = FPDF()

    pdf.add_page()


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    pdf.set_text_color(
        6,
        78,
        59
    )

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

    pdf.ln(8)


    # --------------------------------------------------------
    # USER INFORMATION
    # --------------------------------------------------------

    pdf.set_text_color(
        30,
        41,
        59
    )

    pdf.set_font(
        "Arial",
        style="B",
        size=11
    )

    pdf.cell(
        0,
        8,
        "User Information",
        ln=True
    )

    pdf.set_font(
        "Arial",
        size=11
    )

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


    # --------------------------------------------------------
    # BASELINE MODEL
    # --------------------------------------------------------

    pdf.set_text_color(
        6,
        95,
        70
    )

    pdf.set_font(
        "Arial",
        style="B",
        size=11
    )

    pdf.cell(
        0,
        8,
        "Baseline ML Model Verdict",
        ln=True
    )

    pdf.set_text_color(
        30,
        41,
        59
    )

    pdf.set_font(
        "Arial",
        size=11
    )

    pdf.multi_cell(
        0,
        8,
        clean_text(baseline_text)
    )

    pdf.ln(5)


    # --------------------------------------------------------
    # AI ASSESSMENT
    # --------------------------------------------------------

    pdf.set_text_color(
        6,
        95,
        70
    )

    pdf.set_font(
        "Arial",
        style="B",
        size=11
    )

    pdf.cell(
        0,
        8,
        "AI-Corrected Dietary Assessment",
        ln=True
    )

    pdf.set_text_color(
        30,
        41,
        59
    )

    pdf.set_font(
        "Arial",
        size=11
    )

    pdf.multi_cell(
        0,
        8,
        clean_text(ai_text)
    )

    pdf.ln(12)


    # --------------------------------------------------------
    # DISCLAIMER
    # --------------------------------------------------------

    pdf.set_text_color(
        100,
        116,
        139
    )

    pdf.set_font(
        "Arial",
        size=9
    )

    pdf.multi_cell(
        0,
        6,
        clean_text(
            "Disclaimer: This report is for educational purposes "
            "only and should not replace advice from a qualified "
            "healthcare professional."
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
        "## 🩺 Diabetic Diet Advisory"
    )

    st.markdown(
        '<p class="sidebar-subtitle">'
        'AI + Machine Learning Nutrition Assistant'
        '</p>',
        unsafe_allow_html=True
    )

    st.divider()


    # --------------------------------------------------------
    # HOW IT WORKS
    # --------------------------------------------------------

    st.markdown(
        '<p class="sidebar-section">HOW IT WORKS</p>',
        unsafe_allow_html=True
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
        """,
        unsafe_allow_html=True
    )

    st.divider()


    # --------------------------------------------------------
    # DIETARY FOCUS
    # --------------------------------------------------------

    st.markdown(
        '<p class="sidebar-section">DIETARY FOCUS</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="sidebar-info">
        🌾 Whole grains & millets
        </div>

        <div class="sidebar-info">
        🫘 Fiber-rich foods
        </div>

        <div class="sidebar-info">
        🥗 Portion awareness
        </div>

        <div class="sidebar-info">
        🍬 Limited refined sugar
        </div>

        <div class="sidebar-info">
        🥚 Balanced protein
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.caption(
        "⚠️ Educational project — not a medical diagnostic system."
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.title(
    "🩺 Diabetic Diet Advisory"
)

st.write(
    "Enter your health details and a food item to receive "
    "an AI-assisted, context-aware dietary assessment."
)


# ============================================================
# HEALTH INFORMATION
# ============================================================

st.subheader(
    "👤 Your Health Information"
)

col1, col2, col3, col4 = st.columns(4)


with col1:

    age = st.number_input(
        "🎂 Age",
        min_value=18,
        max_value=90,
        value=45
    )


with col2:

    glucose = st.number_input(
        "🩸 Glucose (mg/dL)",
        min_value=70,
        max_value=300,
        value=140
    )


with col3:

    bmi = st.number_input(
        "⚖️ BMI",
        min_value=15.0,
        max_value=50.0,
        value=25.0,
        step=0.1
    )


with col4:

    bp = st.number_input(
        "❤️ Blood Pressure",
        min_value=60,
        max_value=140,
        value=80
    )


st.markdown("---")


# ============================================================
# FOOD ANALYSIS
# ============================================================

st.subheader(
    "🍽️ Food Analysis"
)

st.info(
    "💡 Tip: Enter the complete meal when possible. "
    "For example: **Bajra roti with 1 tsp ghee and 5g jaggery**."
)

food_item = st.text_input(
    "🥗 Food item eaten",
    placeholder="e.g. Bajra roti with ghee and jaggery"
)


st.write("")


# ============================================================
# ANALYZE FOOD
# ============================================================

if st.button(
    "🔍 Analyze Food"
):

    # --------------------------------------------------------
    # CHECK FOOD INPUT
    # --------------------------------------------------------

    if food_item.strip() == "":

        st.warning(
            "🥗 Please enter a food item before analyzing."
        )

    else:

        # ====================================================
        # BASELINE ML
        # ====================================================

        with st.spinner(
            "🤖 Running baseline machine-learning model..."
        ):

            pred, prob = baseline_predict(
                glucose,
                bmi,
                age,
                bp
            )

            baseline_text = (
                f"{'Higher-risk model signal' if pred == 1 else 'Lower-risk model signal'} "
                f"(model probability: {prob:.0%})"
            )


        # ====================================================
        # BASELINE RESULT
        # ====================================================

        st.subheader(
            "📊 Baseline ML Model Verdict"
        )

        if pred == 1:

            st.error(
                f"""
                ⚠️ **Higher-risk model signal**

                Model probability for class 1:
                **{prob:.0%}**
                """
            )

        else:

            st.success(
                f"""
                ✅ **Lower-risk model signal**

                Model probability for class 1:
                **{prob:.0%}**
                """
            )


        # ====================================================
        # FOOD SELECTED
        # ====================================================

        st.subheader(
            "🍴 Food Selected"
        )

        st.info(
            f"**{food_item}**"
        )


        # ====================================================
        # USER PROFILE
        # ====================================================

        user_profile = (
            f"Age: {age}, "
            f"Glucose: {glucose} mg/dL, "
            f"BMI: {bmi}, "
            f"Blood Pressure: {bp}"
        )


        # ====================================================
        # AI ANALYSIS
        # ====================================================

        with st.spinner(
            "🧠 AI is evaluating the food using dietary guidelines..."
        ):

            ai_text = ai_correct(
                food_item,
                pred,
                prob,
                user_profile
            )


        # ====================================================
        # AI-CORRECTED RESULT
        # ====================================================

        st.subheader(
            "🧠 AI-Corrected Dietary Assessment"
        )


        # ----------------------------------------------------
        # IMPORTANT:
        #
        # html.escape() prevents AI-generated text from
        # accidentally being interpreted as HTML.
        #
        # We also build the HTML WITHOUT indentation.
        # This prevents Streamlit from treating it as a
        # code block.
        # ----------------------------------------------------

        safe_ai_text = html.escape(
            ai_text
        )

        safe_ai_text = safe_ai_text.replace(
            "\n",
            "<br>"
        )


        nutrition_card = (
            '<div class="nutrition-card">'
            '<div class="nutrition-card-title">'
            '✨ Context-Aware Nutrition Insight'
            '</div>'
            '<div class="nutrition-card-body">'
            + safe_ai_text +
            '</div>'
            '</div>'
        )


        st.markdown(
            nutrition_card,
            unsafe_allow_html=True
        )


        # ====================================================
        # WHY AI CORRECTION?
        # ====================================================

        with st.expander(
            "💡 Why does the AI correction layer matter?"
        ):

            st.write(
                """
                The baseline machine-learning model evaluates
                patterns from the health measurements provided.

                However, those measurements alone do not describe
                the complete nutritional composition of a particular
                meal.

                The AI layer adds dietary context such as:

                🌾 **Carbohydrate quality**

                🥗 **Portion size**

                🫘 **Fiber content**

                🥚 **Protein**

                🍬 **Added sugar**

                🧈 **Fat quantity**

                🍽️ **Overall meal composition**
                """
            )


        # ====================================================
        # PDF REPORT
        # ====================================================

        st.subheader(
            "📄 Personalized Report"
        )

        pdf_path = generate_pdf(
            user_profile,
            food_item,
            baseline_text,
            ai_text
        )

        with open(
            pdf_path,
            "rb"
        ) as pdf_file:

            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_file,
                file_name="diet_report.pdf",
                mime="application/pdf"
            )


# ============================================================
# MEDICAL DISCLAIMER
# ============================================================

st.markdown("---")

st.caption(
    "⚠️ **Medical Disclaimer:** This application is an "
    "educational AI/ML project and is not intended to diagnose, "
    "treat, cure, or prevent diabetes. Please consult a qualified "
    "healthcare professional for medical advice."
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
    unsafe_allow_html=True
)
