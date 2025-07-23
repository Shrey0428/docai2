import streamlit as st
import tempfile
import subprocess
from google.oauth2 import service_account
from google.cloud import vision_v1 as vision
from google.cloud.vision_v1 import types

# === Ask LLaMA (local) ===
def ask_llama(prompt, model="llama3"):
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120
        )
        return result.stdout.decode("utf-8")
    except Exception as e:
        return f"❌ LLaMA error: {e}"

# === Extract OCR Text ===
def extract_text_from_pdf(pdf_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(pdf_file.read())
            temp_path = temp.name

        creds_dict = st.secrets["GCP_CREDENTIALS"]
        creds = service_account.Credentials.from_service_account_info(creds_dict)
        client = vision.ImageAnnotatorClient(credentials=creds)

        with open(temp_path, 'rb') as f:
            pdf_content = f.read()

        input_config = types.InputConfig(content=pdf_content, mime_type='application/pdf')
        feature = types.Feature(type_=types.Feature.Type.DOCUMENT_TEXT_DETECTION)
        request = types.AnnotateFileRequest(input_config=input_config, features=[feature])
        response = client.batch_annotate_files(requests=[request])

        all_text = ""
        pages = response.responses[0].responses
        if not pages:
            return None

        for page in pages:
            if page.full_text_annotation.text:
                all_text += page.full_text_annotation.text + "\n"

        return all_text if all_text.strip() else None

    except Exception as e:
        st.error(f"❌ Vision API error: {e}")
        return None

# === Streamlit App ===
st.set_page_config(page_title="DOC AI - PDF Extractor", layout="wide")
st.title("📄 DOC AI — Extract Structured Legal Info from PDF")

uploaded_pdf = st.file_uploader("📤 Upload a scanned legal PDF", type=["pdf"])

if uploaded_pdf:
    with st.spinner("🔍 Extracting text using Google Vision..."):
        extracted_text = extract_text_from_pdf(uploaded_pdf)

    if not extracted_text:
        st.error("❌ Failed to extract text: No text detected. Try a clearer PDF.")
        st.stop()

    st.success("✅ OCR complete!")
    st.subheader("📃 Extracted OCR Text")
    st.text_area("Text Output", extracted_text, height=300)

    if st.button("🔍 Extract Structured Info using LLaMA"):
        prompt = f"""
You are a legal assistant AI. Based on the OCR text below, extract the following:

- Document Type (e.g., Sale Deed, Lease Deed)
- Date of Document
- Names of Buyer and Seller
- Property Address, Plot No, Area
- Witnesses or Signatories
- Registration Numbers or IDs

OCR TEXT:
{extracted_text}
"""
        with st.spinner("🦙 LLaMA is generating structured data..."):
            structured_output = ask_llama(prompt)
            st.subheader("🧾 Structured Data")
            st.text_area("LLaMA Output", structured_output, height=400)
