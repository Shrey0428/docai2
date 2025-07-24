import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import numpy as np
import io

st.set_page_config(page_title="DocAI OCR", page_icon="📄")
st.title("📄 DocAI - OCR PDF Extractor")

uploaded_file = st.file_uploader("📤 Upload a scanned PDF", type="pdf")

def convert_pdf_to_images(pdf_bytes):
    images = []
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                pix = page.get_pixmap(dpi=200)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                images.append(img)
    except Exception as e:
        st.error(f"❌ PDF conversion failed: {e}")
    return images

def extract_text_with_tesseract(images):
    full_text = ""
    for i, img in enumerate(images):
        st.image(img, caption=f"📄 Page {i+1}", use_column_width=True)
        with st.spinner(f"🔍 Extracting text from Page {i+1}..."):
            text = pytesseract.image_to_string(img)
        if not text.strip():
            st.warning(f"⚠️ No text found on page {i+1}.")
        full_text += f"--- Page {i+1} ---\n{text.strip()}\n\n"
    return full_text

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    with st.spinner("📸 Converting PDF to images..."):
        images = convert_pdf_to_images(pdf_bytes)

    if images:
        with st.spinner("🧠 Running OCR..."):
            ocr_text = extract_text_with_tesseract(images)

        st.subheader("📜 Extracted OCR Text")
        st.text_area("Text Output", ocr_text, height=400)
    else:
        st.error("❌ No pages found in PDF.")
else:
    st.info("📥 Upload a scanned PDF to begin.")
