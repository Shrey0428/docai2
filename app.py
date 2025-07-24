import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import easyocr
import numpy as np
import io

st.set_page_config(page_title="DocAI Cloud OCR", page_icon="📄")
st.title("📄 DocAI - Cloud-Based PDF OCR")

# Initialize EasyOCR reader (English)
reader = easyocr.Reader(['en'], gpu=False)

# Upload PDF
uploaded_file = st.file_uploader("📤 Upload a scanned legal PDF", type="pdf")

# Convert PDF pages to images
def pdf_to_images(pdf_bytes):
    images = []
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page_index in range(len(doc)):
                page = doc.load_page(page_index)
                pix = page.get_pixmap(dpi=200)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                images.append(img)
    except Exception as e:
        st.error(f"❌ PDF to image conversion failed: {e}")
    return images

# Extract text using EasyOCR
def extract_text_from_images(images):
    all_text = ""
    for i, img in enumerate(images):
        st.image(img, caption=f"📄 Page {i+1}", use_column_width=True)
        with st.spinner(f"🔍 Running OCR on Page {i+1}..."):
            result = reader.readtext(np.array(img), detail=0)
            page_text = "\n".join(result)
            if not page_text.strip():
                st.warning(f"⚠️ No text detected on page {i+1}.")
            all_text += page_text + "\n"
    return all_text.strip()

# Dummy structured extractor
def structured_extraction(text):
    if not text:
        return {}
    return {
        "Party Name": "John Doe",
        "Document Type": "Lease Deed",
        "Date": "15-Feb-2023",
        "Location": "Hyderabad",
        "Amount": "₹18,00,000"
    }

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    with st.spinner("📸 Converting PDF pages to images..."):
        images = pdf_to_images(pdf_bytes)

    if images:
        st.success("✅ PDF successfully converted to images.")
        with st.spinner("🧠 Performing OCR..."):
            text = extract_text_from_images(images)

        if text:
            st.subheader("📜 Extracted OCR Text")
            st.text_area("Full OCR Output", text, height=300)

            st.subheader("📋 Structured Data (Demo)")
            data = structured_extraction(text)
            st.json(data)
        else:
            st.error("❌ OCR failed or no text found.")
    else:
        st.error("❌ Could not convert PDF to images.")
else:
    st.info("📥 Please upload a scanned PDF to begin OCR.")
