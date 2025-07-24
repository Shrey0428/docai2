import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
from google.cloud import vision
from google.oauth2 import service_account
import io
import os

st.set_page_config(page_title="DocAI", layout="wide")
st.title("📄 DocAI – Scan & Extract Text from PDFs")

# Load credentials from secrets
creds_dict = st.secrets["google"]
credentials = service_account.Credentials.from_service_account_info(creds_dict)
client = vision.ImageAnnotatorClient(credentials=credentials)

# Upload PDF
uploaded_file = st.file_uploader("📤 Upload a scanned PDF", type=["pdf"])

# PDF to Images
def convert_pdf_to_images(pdf_bytes):
    images = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        images.append(img)
    return images

# OCR via Google Vision
def extract_text_with_vision(image: Image.Image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    content = img_byte_arr.getvalue()
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    return response.full_text_annotation.text

if uploaded_file:
    images = convert_pdf_to_images(uploaded_file.read())
    st.success(f"✅ Converted {len(images)} page(s) to images.")
    full_text = ""

    for idx, img in enumerate(images):
        st.image(img, caption=f"📃 Page {idx+1}", use_column_width=True)
        with st.spinner(f"🔍 Extracting text from Page {idx+1}..."):
            try:
                text = extract_text_with_vision(img)
                if not text.strip():
                    st.warning("⚠️ No text detected.")
                else:
                    st.success("✅ Text extracted.")
                    full_text += f"--- Page {idx+1} ---\n{text}\n\n"
            except Exception as e:
                st.error(f"❌ Vision API error: {e}")

    if full_text:
        st.subheader("📋 Extracted Text")
        st.text_area("OCR Result", full_text, height=400)
    else:
        st.warning("⚠️ No text extracted.")
