import os
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import streamlit_shadcn_ui as ui
from openai import OpenAI
from dotenv import load_dotenv
import pdfplumber
import base64

# **Set up Streamlit Page Configuration**
st.set_page_config(page_title="AI Financial Report Chatbot", layout="wide")
st.title("AI powered financial report analysis")
st.subheader("Pdf view and integrated chatbot for summary and questions answer interactions")


# Load API Key from Environment Variable
load_dotenv("chat.env")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Ensure API Key is provided
if not openai_api_key:
    st.error("⚠️ OpenAI API key is missing! Please set it in a `.env` file.")
    st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# **Function to Extract Text from PDF**
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    return text

# **Function to Summarize Financial Report**
def summarize_financial_report(text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a financial analyst. Provide a very short summary of the company's financial health based on the following financial report."},
            {"role": "user", "content": f"Summarize this financial report:\n{text}"}
        ]
    )
    return response.choices[0].message.content.strip()

# **Function to Answer Financial Questions**
def answer_financial_question(text, question):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a financial analyst answering questions about financial reports."},
            {"role": "user", "content": f"Document:\n{text}\n\nQuestion: {question}"}
        ]
    )
    return response.choices[0].message.content.strip()

# **Function to Show PDF**
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="900px"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# **List available PDFs in the directory**
pdf_files = [f for f in os.listdir() if f.endswith(".pdf")]

if not pdf_files:
    st.warning("No PDF files found in the directory. Please upload some reports.")
    st.stop()

# **Dropdown to Select PDF**
st.subheader("📄 Select a Financial Report")
selected_pdf = ui.select(options=pdf_files)

# **Streamlit Layout: PDF Viewer & Analysis**
col4, col5 = st.columns([3, 2])

# **PDF Viewer Column**
with col4:
    st.subheader("📄 PDF Viewer")
    show_pdf(selected_pdf)

# **Right Column: Summary & Chatbot**
with col5:
    st.subheader("📈 Financial Summary")

    # Use session state to persist summary
    if "summary" not in st.session_state:
        st.session_state.summary = None

    # **Summarize Report Button**
    clicked = ui.button("Summarize Report", key="summarize_button")

    if clicked or st.session_state.summary:
        if clicked:
            st.session_state.summary = summarize_financial_report(extract_text_from_pdf(selected_pdf))

        # Display summary inside a card
        with ui.card(key="summary_card"):
            ui.element("p", children=[st.session_state.summary], className="text-gray-600 text-sm")

    # **Ask a Question Section**
    st.subheader("💬 Ask a question about the financial report")

    # Store last question and answer
    if "last_answer" not in st.session_state:
        st.session_state.last_answer = None

    question = st.text_input("Type your question here:")

    if ui.button("Ask", key="ask_button") and question:
        st.session_state.last_answer = answer_financial_question(extract_text_from_pdf(selected_pdf), question)

    if st.session_state.last_answer:
        with ui.card(key="answer_card"):
            ui.element("p", children=[st.session_state.last_answer], className="text-gray-600 text-sm")
