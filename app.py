import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import numpy as np
import io

st.set_page_config(page_title="DocAI - PDF OCR", layout="wide")
st.title("📄 DocAI - PDF Scanner & OCR")

uploaded_file = st.file_uploader("📤 Upload a scanned PDF", type=["pdf"])

def convert_pdf_to_images(pdf_bytes):
    images = []
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            images.append(img)
    except Exception as e:
        st.error(f"❌ PDF conversion failed: {e}")
    return images

def extract_text_with_tesseract(images):
    extracted_text = ""
    for idx, img in enumerate(images):
        st.image(img, caption=f"📃 Page {idx+1}", use_column_width=True)
        with st.spinner(f"🔍 OCR for Page {idx+1}..."):
            text = pytesseract.image_to_string(img)
        if not text.strip():
            st.warning(f"⚠️ No text found on Page {idx+1}")
        extracted_text += f"--- Page {idx+1} ---\n{text.strip()}\n\n"
    return extracted_text

if uploaded_file:
    st.subheader("📸 Step 1: Convert PDF to Images")
    with st.spinner("Processing PDF..."):
        images = convert_pdf_to_images(uploaded_file.read())

    if images:
        st.success(f"✅ Converted {len(images)} page(s).")
        st.subheader("🧠 Step 2: Extracting Text with OCR")
        ocr_text = extract_text_with_tesseract(images)
        st.subheader("📋 Step 3: Extracted Text")
        st.text_area("OCR Output", ocr_text, height=400)
    else:
        st.error("❌ No images extracted from PDF.")
else:
    st.info("📥 Upload a scanned PDF to begin.")
