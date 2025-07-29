import os
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from openai import OpenAI
from dotenv import load_dotenv
import pdfplumber
import base64

# --- Set up Streamlit Page Configuration ---
st.set_page_config(page_title="AI Financial Report Chatbot", layout="wide")
st.title("AI powered financial report analysis")
st.subheader("Pdf view and integrated chatbot for summary and questions answer interactions")

# --- Load API Key from environment ---
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    st.error("⚠️ OpenAI API key is missing! Please set it in a `.env` file or in Render environment.")
    st.stop()

# --- Initialize OpenAI client ---
client = OpenAI(api_key=openai_api_key)

# --- PDF text extractor ---
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

# --- Summarize financial report ---
def summarize_financial_report(text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a financial analyst. Provide a very short summary of the company's financial health based on the following financial report."},
            {"role": "user", "content": f"Summarize this financial report:\n{text}"}
        ]
    )
    return response.choices[0].message.content.strip()

# --- Answer financial question ---
def answer_financial_question(text, question):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a financial analyst answering questions about financial reports."},
            {"role": "user", "content": f"Document:\n{text}\n\nQuestion: {question}"}
        ]
    )
    return response.choices[0].message.content.strip()

# --- Display PDF ---
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="900px"></iframe>', unsafe_allow_html=True)

# --- Find PDFs ---
pdf_files = [f for f in os.listdir() if f.endswith(".pdf")]
if not pdf_files:
    st.warning("No PDF files found in the directory. Please upload some reports.")
    st.stop()

# --- Select a file ---
st.subheader("📄 Select a Financial Report")
selected_pdf = st.selectbox("Choose a report:", pdf_files)

# --- Layout ---
col1, col2 = st.columns([3, 2])

# --- PDF Viewer ---
with col1:
    st.subheader("📄 PDF Viewer")
    show_pdf(selected_pdf)

# --- Summary & Chatbot ---
with col2:
    st.subheader("📈 Financial Summary")

    if "summary" not in st.session_state:
        st.session_state.summary = None

    if st.button("Summarize Report"):
        st.session_state.summary = summarize_financial_report(extract_text_from_pdf(selected_pdf))

    if st.session_state.summary:
        st.info(st.session_state.summary)

    st.subheader("💬 Ask a question about the financial report")

    if "last_answer" not in st.session_state:
        st.session_state.last_answer = None

    question = st.text_input("Type your question here:")

    if st.button("Ask") and question:
        st.session_state.last_answer = answer_financial_question(extract_text_from_pdf(selected_pdf), question)

    if st.session_state.last_answer:
        st.success(st.session_state.last_answer)
