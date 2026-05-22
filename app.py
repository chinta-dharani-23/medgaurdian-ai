# ============================================
# MEDGUARDIAN AI
# Advanced Medical Assistant
# Google Colab + Gradio + Gemini
# ============================================

# INSTALL REQUIRED LIBRARIES


# ============================================
# IMPORTS
# ============================================

import gradio as gr
from google import genai
from PIL import Image
import fitz
import os
import tempfile

# ============================================
# GEMINI CLIENT
# ============================================

# OPTION 1:
# client = genai.Client(api_key="YOUR_API_KEY")

# OPTION 2 (Colab Authenticated)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ============================================
# SYSTEM PROMPT
# ============================================

SYSTEM_PROMPT = """
You are MedGuardian AI - a responsible AI Medical Assistant.

IMPORTANT RULES:
- You are NOT a doctor.
- Provide educational guidance only.
- Never provide dangerous medical advice.
- Encourage consulting healthcare professionals.
- If symptoms appear serious, say:
  "Seek immediate medical attention."

BEHAVIOR:
- Use simple patient-friendly language.
- Be empathetic and professional.
- Mention uncertainty when needed.
- Never diagnose with certainty.
- Respect privacy.

CAPABILITIES:
- Symptom guidance
- Medical report explanation
- Medicine information
- Lifestyle suggestions
- Basic image understanding
- Emergency warning detection

RED FLAGS:
Chest pain, stroke symptoms, severe breathing issues,
heavy bleeding, suicidal thoughts, unconsciousness,
severe allergic reactions, seizures, high fever in infants.

FORMAT:
1. Possible Understanding
2. Important Notes
3. Suggested Next Steps
4. Emergency Warning (if needed)
5. Disclaimer
"""

# ============================================
# PDF TEXT EXTRACTION
# ============================================

def extract_text_from_pdf(pdf_file):

    text = ""

    try:
        pdf_document = fitz.open(pdf_file.name)

        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()

        pdf_document.close()

    except Exception as e:
        text = f"Error reading PDF: {str(e)}"

    return text


# ============================================
# MAIN ANALYSIS FUNCTION
# ============================================

def analyze_medical_query(message, medical_image=None, report_file=None):

    try:

        content_parts = []

        # USER QUERY
        if message:
            content_parts.append(
                f"""
Patient Query:
{message}
"""
            )

        # IMAGE ANALYSIS
        if medical_image is not None:

            pil_image = Image.fromarray(medical_image)

            content_parts.append(pil_image)

            content_parts.append("""
Analyze this medical image carefully.

IMPORTANT:
- Do NOT provide final diagnosis.
- Mention visible observations.
- Mention possible concerns.
- Mention whether medical consultation is recommended.
- Mention emergency signs if visible.
""")

        # REPORT FILE ANALYSIS
        if report_file is not None:

            file_name = report_file.name.lower()

            # PDF SUPPORT
            if file_name.endswith(".pdf"):

                report_text = extract_text_from_pdf(report_file)

                content_parts.append(
                    f"""
Medical Report Content:
{report_text}

Explain this report in simple language.
Mention abnormal findings.
Mention doctor specialty recommendation.
"""
                )

            # IMAGE REPORT SUPPORT
            elif (
                file_name.endswith(".png")
                or file_name.endswith(".jpg")
                or file_name.endswith(".jpeg")
                or file_name.endswith(".webp")
            ):

                report_image = Image.open(report_file.name)

                content_parts.append(report_image)

                content_parts.append("""
This is a medical report image.

Extract and explain:
- Important values
- Abnormal findings
- What it may indicate
- Which doctor may help

Explain in very simple language.
""")

        # FINAL PROMPT
        final_prompt = SYSTEM_PROMPT + "\n\n"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[final_prompt] + content_parts
        )

        return response.text

    except Exception as e:
        return f"Error: {str(e)}"


# ============================================
# CHATBOT RESPONSE
# ============================================

def chatbot_response(message, history, image, report):

    response = analyze_medical_query(
        message=message,
        medical_image=image,
        report_file=report
    )

    history.append(
        {
            "role": "user",
            "content": message
        }
    )

    history.append(
        {
            "role": "assistant",
            "content": response
        }
    )

    return history, "", None, None


# ============================================
# CUSTOM CSS
# ============================================

custom_css = """
:root {
    --bg: #f6f8fb;
    --panel: #ffffff;
    --ink: #142033;
    --muted: #637083;
    --line: #dbe3ee;
    --brand: #0f766e;
    --brand-dark: #115e59;
    --accent: #2563eb;
    --danger: #b42318;
    --danger-bg: #fff3f0;
    --privacy-bg: #ecfdf5;
    --feature-bg: #f8fafc;
}

body {
    background: var(--bg);
}

.gradio-container {
    background: linear-gradient(180deg, #eef7f6 0%, #f6f8fb 34%, #ffffff 100%);
    color: var(--ink) !important;
    min-height: 100vh;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.main {
    max-width: 1180px !important;
    margin: 0 auto !important;
    padding: 28px 18px 22px !important;
}

.app-hero {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    margin-bottom: 18px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(20, 32, 51, 0.10);
}

.kicker {
    color: var(--brand);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.main-title {

    text-align: center;

    font-size: 54px;

    font-weight: 900;

    margin-top: 10px;

    margin-bottom: 6px;

    background:
    linear-gradient(
        90deg,
        #38bdf8,
        #14b8a6,
        #06b6d4
    );

    -webkit-background-clip: text;

    -webkit-text-fill-color: transparent;
}

.subtitle {
    color: var(--muted);
    font-size: 16px;
    line-height: 1.55;
    max-width: 680px;
    margin-top: 10px;
}

.status-pill {
    flex: 0 0 auto;
    border: 1px solid rgba(15, 118, 110, 0.24);
    background: #ffffff;
    color: var(--brand-dark);
    border-radius: 999px;
    padding: 9px 13px;
    font-size: 13px;
    font-weight: 800;
    box-shadow: 0 10px 26px rgba(15, 23, 42, 0.08);
}

.workspace-row {
    gap: 18px !important;
    align-items: stretch !important;
}

.glass-box {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 18px;
    box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
}

.info-card {
    border-radius: 8px;
    padding: 16px;
    border: 1px solid var(--line);
    color: var(--ink) !important;
    line-height: 1.55;
    font-size: 14px;
    margin-bottom: 14px;
}

.info-card:last-child {
    margin-bottom: 0;
}

.info-card b {
    display: block;
    margin-bottom: 8px;
    color: var(--ink) !important;
    font-size: 13px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.disclaimer-box {
    background: var(--danger-bg);
    border-color: #ffd0c7;
}

.disclaimer-box b {
    color: var(--danger) !important;
}

.privacy-box {
    background: var(--privacy-bg);
    border-color: #bbf7d0;
}

.privacy-box b {
    color: var(--brand-dark) !important;
}

.feature-box {
    background: var(--feature-bg);
}

.feature-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
    margin-top: 10px;
}

.feature-item {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--ink) !important;
}

.feature-dot {
    width: 7px;
    height: 7px;
    border-radius: 999px;
    background: var(--brand);
    flex: 0 0 auto;
}

.chatbot {
    border: 1px solid var(--line) !important;
    border-radius: 8px !important;
    overflow: hidden;
    background: #ffffff !important;
}

label, .wrap, .prose, .gr-form, .gr-box, .gr-panel {
    color: var(--ink) !important;
}

textarea,
input {
    color: var(--ink) !important;
    background: #ffffff !important;
    border-color: var(--line) !important;
}

textarea::placeholder {
    color: #7b8797 !important;
}

button {
    border-radius: 8px !important;
    font-weight: 800 !important;
    transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
}

button:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 22px rgba(15, 23, 42, 0.10);
}

.footer-text {
    text-align: center;
    color: var(--muted);
    margin-top: 16px;
    font-size: 13px;
}

.sample-questions {
    color: var(--muted);
    font-size: 13px;
    margin-top: 8px;
    font-weight: 700;
}

.sample-questions label {
    color: var(--ink) !important;
    font-weight: 800 !important;
}

.sample-questions .wrap {
    background: #ffffff !important;
    border-color: var(--line) !important;
}

@media (max-width: 860px) {
    .main {
        padding: 20px 12px !important;
    }

    .app-hero {
        display: block;
    }

    .main-title {
        font-size: 34px;
    }

    .status-pill {
        display: inline-block;
        margin-top: 14px;
    }
}
"""

# ============================================
# UI DESIGN
# ============================================

with gr.Blocks(
    css=custom_css,
    theme=gr.themes.Soft(
        primary_hue="teal",
        secondary_hue="blue",
        neutral_hue="slate"
    )
) as demo:

    gr.HTML(
        """
        <section class='app-hero'>
            <div>
                <h3>Responsible healthcare assistant</h3>
                <h1 class='main-title'>🩺 MedGuardian AI</h1>
                <h4>A clean medical support workspace for symptoms, reports, medicines, and image-based health questions.</h4>
            </div>
        </section>
        """
    )

    with gr.Row(equal_height=True, elem_classes="workspace-row"):

        # ============================================
        # LEFT SIDE
        # ============================================

        with gr.Column(scale=1, min_width=280):

            with gr.Group(elem_classes="glass-box"):

                gr.HTML(
                    """
                    <div class='info-card disclaimer-box'>
                        <b>Important disclaimer</b>
                        This assistant provides educational and preliminary support only. It is not a substitute for a licensed medical professional. In emergencies, contact emergency services immediately.
                    </div>
                    """
                )

                gr.HTML(
                    """
                    <div class='info-card privacy-box'>
                        <b>Privacy notice</b>
                        Avoid uploading highly sensitive personal information. Share reports and images only when needed for the question.
                    </div>
                    """
                )

                gr.HTML(
                    """
                    <div class='info-card feature-box'>
                        <b>What it can help with</b>
                        <div class='feature-grid'>
                            <div class='feature-item'><span class='feature-dot'></span> Symptom guidance</div>
                            <div class='feature-item'><span class='feature-dot'></span> Medical report explanation</div>
                            <div class='feature-item'><span class='feature-dot'></span> Report and skin image review</div>
                            <div class='feature-item'><span class='feature-dot'></span> Medicine information</div>
                            <div class='feature-item'><span class='feature-dot'></span> Emergency red flag detection</div>
                            <div class='feature-item'><span class='feature-dot'></span> Patient-friendly explanations</div>
                        </div>
                    </div>
                    """
                )
                sample_question = gr.Radio(
                    choices=[
                        "I have fever and sore throat for 3 days",
                        "Explain my blood test report",
                        "What are symptoms of diabetes?",
                        "I have chest pain and difficulty breathing",
                        "Explain side effects of paracetamol",
                        "Analyze my skin image",
                    ],
                    label="Sample questions",
                    value=None,
                    elem_classes="sample-questions"
                )
                gr.HTML(
                    """
                    <div class='status-pill'>Educational guidance only</div>
                    """
                )
                

        # ============================================
        # RIGHT SIDE
        # ============================================

        with gr.Column(scale=2, min_width=420):

            with gr.Group(elem_classes="glass-box"):

                chatbot = gr.Chatbot(
                    type="messages",
                    height=540,
                    label="Medical AI Conversation",
                    elem_classes="chatbot"
                )

                user_input = gr.Textbox(
                    placeholder="Describe symptoms, upload a report, or ask a medical question...",
                    lines=3,
                    label="Patient Query"
                )

                with gr.Row():

                    image_input = gr.Image(
                        type="numpy",
                        label="Upload Medical Image"
                    )

                    report_input = gr.File(
                        label="Upload Medical Report",
                        file_types=[
                            ".pdf",
                            ".png",
                            ".jpg",
                            ".jpeg",
                            ".webp"
                        ]
                    )

                with gr.Row():

                    send_btn = gr.Button(
                        "Analyze",
                        variant="primary",
                        scale=3
                    )

                    clear_btn = gr.Button(
                        "Clear",
                        scale=1
                    )


    gr.HTML(
        """
        <div class='footer-text'>
            MedGuardian AI - Responsible AI healthcare support
        </div>
        """
    )

    # ============================================
    # BUTTON ACTIONS
    # ============================================

    sample_question.change(
        lambda question: question or "",
        inputs=sample_question,
        outputs=user_input
    )
    send_btn.click(
        chatbot_response,
        inputs=[
            user_input,
            chatbot,
            image_input,
            report_input
        ],
        outputs=[
            chatbot,
            user_input,
            image_input,
            report_input
        ]
    )

    clear_btn.click(
        lambda: ([], "", None, None),
        outputs=[
            chatbot,
            user_input,
            image_input,
            report_input
        ]
    )

# ============================================
# LAUNCH APP
# ============================================

demo.launch(
    server_name="0.0.0.0",
    server_port=7860
)