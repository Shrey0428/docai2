import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract
import tempfile
import os

st.set_page_config(page_title="DocAI - Local OCR", page_icon="📄")
st.title("📄 DocAI - Offline OCR & Analysis")

# Set Tesseract path if needed (uncomment and modify below on Windows)
# pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Upload PDF
uploaded_file = st.file_uploader("Upload a scanned legal PDF", type=["pdf"])

# Extract text using pytesseract OCR
def extract_text_from_pdf(pdf_bytes):
    try:
        images = convert_from_bytes(pdf_bytes)
        all_text = ""

        for idx, img in enumerate(images):
            st.image(img, caption=f"📄 Page {idx + 1}", use_column_width=True)

            # Convert to grayscale for better OCR
            gray = img.convert("L")
            text = pytesseract.image_to_string(gray)

            if not text.strip():
                st.warning(f"⚠️ No text detected on Page {idx + 1}. Try a clearer scan.")
            else:
                all_text += text + "\n"

        if not all_text.strip():
            st.error("❌ No text detected on any page. Try a better scanned PDF.")
            return None

        return all_text

    except Exception as e:
        st.error(f"❌ OCR failed: {e}")
        return None

# Dummy structured extractor using LLaMA (placeholder)
def structured_extraction_llama(raw_text):
    return {
        "Party Name": "John Doe",
        "Document Type": "Lease Deed",
        "Date": "15-Feb-2023",
        "Location": "Hyderabad",
        "Amount": "₹18,00,000"
    } if raw_text else {}

if uploaded_file:
    with st.spinner("🔍 Extracting text using Tesseract OCR..."):
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
        st.error("❌ No text found. Please upload a clearer scanned PDF.")
else:
    st.info("📤 Please upload a scanned legal PDF to begin.")
