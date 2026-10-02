# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Diabetic Diet Advisory",
    page_icon="🩺",
    layout="wide"
)


# ============================================================
# PROFESSIONAL COLOR / GRADIENT CSS
# ============================================================

st.markdown("""
<style>

    /* =====================================================
       MAIN APP BACKGROUND
       ===================================================== */

    .stApp {
        background:
            linear-gradient(
                135deg,
                #F0FDF9 0%,
                #E8F8F3 45%,
                #F3F7FF 100%
            );
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }


    /* =====================================================
       MAIN TITLE
       ===================================================== */

    h1 {
        color: #064E3B !important;
        font-weight: 800 !important;
        font-size: 42px !important;
        letter-spacing: -1px;
    }

    h2, h3 {
        color: #065F46 !important;
        font-weight: 750 !important;
    }

    p {
        color: #475569;
    }


    /* =====================================================
       INPUT LABELS
       ===================================================== */

    label {
        color: #064E3B !important;
        font-weight: 650 !important;
    }


    /* =====================================================
       NUMBER INPUTS
       ===================================================== */

    div[data-testid="stNumberInput"] > div {
        background: rgba(255,255,255,0.85);
        border-radius: 14px;
    }

    div[data-testid="stNumberInput"] input {
        border-radius: 14px !important;
        border: 1px solid #B7DED0 !important;
        background: white !important;
        color: #064E3B !important;
        font-weight: 600 !important;
    }

    div[data-testid="stNumberInput"] input:focus {
        border: 2px solid #10B981 !important;
        box-shadow: 0 0 0 3px rgba(16,185,129,0.12) !important;
    }


    /* =====================================================
       TEXT INPUT
       ===================================================== */

    div[data-testid="stTextInput"] input {
        border-radius: 14px !important;
        border: 1px solid #B7DED0 !important;
        background: white !important;
        color: #064E3B !important;
        padding: 14px !important;
        font-size: 16px !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border: 2px solid #10B981 !important;
        box-shadow: 0 0 0 3px rgba(16,185,129,0.12) !important;
    }


    /* =====================================================
       ANALYZE BUTTON
       ===================================================== */

    div.stButton > button {
        width: 100%;

        background:
            linear-gradient(
                135deg,
                #047857 0%,
                #10B981 50%,
                #14B8A6 100%
            );

        color: white !important;

        border: none !important;

        border-radius: 14px !important;

        padding: 13px 20px !important;

        font-size: 17px !important;

        font-weight: 700 !important;

        box-shadow:
            0 8px 20px rgba(5,150,105,0.22);

        transition: all 0.25s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);

        box-shadow:
            0 12px 25px rgba(5,150,105,0.30);

        background:
            linear-gradient(
                135deg,
                #065F46,
                #059669,
                #0D9488
            );
    }


    /* =====================================================
       DOWNLOAD BUTTON
       ===================================================== */

    div.stDownloadButton > button {

        width: 100%;

        background:
            linear-gradient(
                135deg,
                #334155,
                #475569
            );

        color: white !important;

        border: none !important;

        border-radius: 14px !important;

        padding: 12px !important;

        font-weight: 700 !important;

        box-shadow:
            0 6px 16px rgba(51,65,85,0.18);
    }

    div.stDownloadButton > button:hover {
        background:
            linear-gradient(
                135deg,
                #1E293B,
                #475569
            );
    }


    /* =====================================================
       EXPANDER
       ===================================================== */

    div[data-testid="stExpander"] {
        border: 1px solid #CDE9DE !important;
        border-radius: 15px !important;
        background: rgba(255,255,255,0.75);
    }


    /* =====================================================
       ALERT BOXES
       ===================================================== */

    div[data-testid="stAlert"] {
        border-radius: 14px !important;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #064E3B 0%,
                #065F46 45%,
                #047857 100%
            );
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }


    /* =====================================================
       DIVIDER
       ===================================================== */

    hr {
        border: none;
        height: 1px;
        background:
            linear-gradient(
                90deg,
                transparent,
                #8FD8C2,
                transparent
            );
    }


    /* =====================================================
       RESULT CONTAINERS
       ===================================================== */

    .result-box {
        padding: 20px;
        border-radius: 16px;
        margin: 10px 0;
    }


    /* =====================================================
       SCROLLBAR
       ===================================================== */

    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #E8F8F3;
    }

    ::-webkit-scrollbar-thumb {
        background: #10B981;
        border-radius: 10px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🩺 Diet Advisory")

    st.caption("AI + Machine Learning")

    st.divider()

    st.markdown("### 🔬 How it works")

    st.markdown("""
    **🤖 Step 1**  
    ML model analyzes health inputs.

    **🍽️ Step 2**  
    Enter the food or meal.

    **🧠 Step 3**  
    AI evaluates the dietary context.

    **📊 Step 4**  
    Receive a personalized assessment.
    """)

    st.divider()

    st.markdown("### 🌱 Dietary Focus")

    st.markdown("""
    🌾 Whole grains & millets

    🫘 Fiber-rich foods

    🥗 Balanced portions

    🍬 Limited refined sugar

    💧 Healthy meal composition
    """)

    st.divider()

    st.caption(
        "⚠️ Educational project — "
        "not a medical diagnosis."
    )


# ============================================================
# TITLE
# ============================================================

st.title("🩺 Diabetic Diet Advisory")

st.write(
    "Enter your health details and a food item to receive "
    "an AI-assisted, context-aware dietary assessment."
)


# ============================================================
# USER INFORMATION
# ============================================================

st.subheader("👤 Your Health Information")

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
# FOOD INPUT
# ============================================================

st.subheader("🍽️ Food Analysis")

st.info(
    "💡 Enter a complete meal when possible. "
    "For example: **Bajra roti with 1 tsp ghee and jaggery**."
)

food_item = st.text_input(
    "🥗 Food item eaten",
    placeholder="e.g. Bajra roti with ghee and jaggery"
)


st.write("")


# ============================================================
# ANALYZE BUTTON
# ============================================================

if st.button("🔍 Analyze Food"):

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
                f"{'High diabetes risk' if pred == 1 else 'Low diabetes risk'} "
                f"(confidence: {prob:.0%})"
            )


        # ====================================================
        # BASELINE RESULT
        # ====================================================

        st.subheader("📊 Baseline ML Model Verdict")

        if pred == 1:

            st.error(
                f"⚠️ **High Risk Signal**\n\n"
                f"Model probability for class 1: **{prob:.0%}**"
            )

        else:

            st.success(
                f"✅ **Low Risk Signal**\n\n"
                f"Model probability for class 1: **{prob:.0%}**"
            )


        # ====================================================
        # FOOD SUMMARY
        # ====================================================

        st.markdown("### 🍴 Food Selected")

        st.info(
            f"**{food_item}**"
        )


        # ====================================================
        # AI CORRECTION
        # ====================================================

        user_profile = (
            f"Age {age}, "
            f"Glucose {glucose} mg/dL, "
            f"BMI {bmi}, "
            f"BP {bp}"
        )

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
        # AI RESULT
        # ====================================================

        st.subheader("🧠 AI-Corrected Dietary Assessment")

        st.success(
            f"✨ **Context-Aware Nutrition Insight**\n\n"
            f"{ai_text}"
        )


        # ====================================================
        # EXPLANATION
        # ====================================================

        with st.expander(
            "💡 Why is there an AI correction layer?"
        ):

            st.write(
                """
                The baseline machine-learning model evaluates
                patterns in the health measurements.

                However, a food item cannot necessarily be classified
                as appropriate or inappropriate from those measurements
                alone.

                The AI layer adds dietary context such as:

                - 🌾 Carbohydrate quality
                - 🥗 Portion size
                - 🫘 Fiber content
                - 🥚 Protein
                - 🍬 Added sugar
                - 🧈 Fat quantity
                - 🍽️ Overall meal composition

                This allows the application to provide a more
                context-aware dietary explanation.
                """
            )


        # ====================================================
        # PDF
        # ====================================================

        st.subheader("📄 Your Report")

        pdf_path = generate_pdf(
            user_profile,
            food_item,
            baseline_text,
            ai_text
        )

        with open(pdf_path, "rb") as f:

            st.download_button(
                "📥 Download Personalized PDF Report",
                f,
                file_name="diet_report.pdf",
                mime="application/pdf"
            )


# ============================================================
# FOOTER / DISCLAIMER
# ============================================================

st.markdown("---")

st.caption(
    "⚠️ **Medical Disclaimer:** This application is an "
    "educational AI/ML project and is not intended to diagnose, "
    "treat, cure, or prevent diabetes. Consult a qualified "
    "healthcare professional for medical advice."
)

st.caption(
    "🩺 Diabetic Diet Advisory • Built with Python, "
    "Streamlit, Machine Learning & Generative AI"
)
