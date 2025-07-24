import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import easyocr
import numpy as np
import io

st.set_page_config(page_title="DocAI", page_icon="📄")

st.title("📄 DocAI - OCR PDF Extractor")

reader = easyocr.Reader(['en'], gpu=False)

uploaded_file = st.file_uploader("📤 Upload scanned PDF", type="pdf")

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    images = []
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for i in range(len(doc)):
                page = doc.load_page(i)
                pix = page.get_pixmap(dpi=200)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                images.append(img)
    except Exception as e:
        st.error(f"Error loading PDF: {e}")

    st.success("✅ Converted to images")

    full_text = ""
    for i, img in enumerate(images):
        st.image(img, caption=f"Page {i+1}")
        result = reader.readtext(np.array(img), detail=0)
        text = "\n".join(result)
        st.text_area(f"OCR Text for Page {i+1}", text, height=150)
        full_text += text + "\n"

    st.subheader("📋 Combined Extracted Text")
    st.text_area("All Text", full_text, height=300)
else:
    st.info("Please upload a scanned PDF file.")
