import streamlit as st
import os
from google.oauth2 import service_account
from google.cloud import vision_v1 as vision
from google.cloud.vision_v1 import types
from pdf2image import convert_from_bytes
import tempfile

st.set_page_config(page_title="DocAI OCR", page_icon="📄")
st.title("📄 Document OCR & Analysis")

# Upload PDF
uploaded_file = st.file_uploader("Upload a scanned legal PDF", type=["pdf"])

# Extract text from PDF using Google Cloud Vision API
def extract_text_from_pdf(pdf_bytes):
    try:
        creds = service_account.Credentials.from_service_account_info(st.secrets["GCP_CREDENTIALS"])
        client = vision.ImageAnnotatorClient(credentials=creds)

        # Convert PDF pages to images
        images = convert_from_bytes(pdf_bytes)
        all_text = ""

        for img in images:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                img.save(tmp.name, format='PNG')
                with open(tmp.name, 'rb') as f:
                    image = vision.Image(content=f.read())
                    response = client.document_text_detection(image=image)

                    if response.error.message:
                        st.error(f"❌ Vision API error: {response.error.message}")
                        return ""

                    annotation = response.full_text_annotation.text
                    if annotation:
                        all_text += annotation + "\n"

                os.remove(tmp.name)

        return all_text if all_text.strip() else None

    except Exception as e:
        st.error(f"❌ Failed to extract text: {e}")
        return None

# Dummy structured extractor using LLaMA (placeholder)
def structured_extraction_llama(raw_text):
    # Replace this with your real local LLaMA call or API later
    return {
        "Party Name": "John Doe",
        "Document Type": "Sale Deed",
        "Date": "01-Jan-2022",
        "Location": "Delhi",
        "Amount": "₹25,00,000"
    } if raw_text else {}

if uploaded_file:
    with st.spinner("🔍 Extracting text using Google Vision API..."):
        raw_text = extract_text_from_pdf(uploaded_file.read())

    if raw_text:
        st.success("✅ Text successfully extracted!")
        st.subheader("📜 Raw OCR Text")
        st.text_area("Extracted Text", raw_text, height=300)

        with st.spinner("🤖 Analyzing with LLaMA model..."):
            data = structured_extraction_llama(raw_text)

        st.subheader("📋 Structured Legal Info")
        st.json(data)
    else:
        st.error("❌ No text detected. Try a clearer PDF.")
else:
    st.info("📤 Please upload a scanned legal PDF to get started.")
