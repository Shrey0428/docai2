import streamlit as st
import tempfile
import subprocess
from google.oauth2 import service_account
from google.cloud import vision_v1 as vision
from google.cloud.vision_v1 import types

# === Ask LLaMA (via Ollama) ===
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
        return f"❌ Error calling LLaMA: {e}"

# === Extract text from PDF using Google Vision ===
def extract_text_from_pdf(pdf_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        temp.write(pdf_file.read())
        temp_path = temp.name

    # Load GCP credentials from Streamlit secrets
    creds_dict = st.secrets["GCP_CREDENTIALS"]
    creds = service_account.Credentials.from_service_account_info(creds_dict)

    client = vision.ImageAnnotatorClient(credentials=creds)

    # Read the file content
    with open(temp_path, 'rb') as f:
        pdf_content = f.read()

    input_config = types.InputConfig(content=pdf_content, mime_type='application/pdf')
    feature = types.Feature(type_=types.Feature.Type.DOCUMENT_TEXT_DETECTION)
    request = types.AnnotateFileRequest(input_config=input_config, features=[feature])

    response = client.batch_annotate_files(requests=[request])
    all_text = ""
    for page in response.responses[0].responses:
        if page.full_text_annotation.text:
            all_text += page.full_text_annotation.text + "\n"
    return all_text

# === Streamlit UI ===
st.set_page_config(page_title="DOC AI - PDF Extractor", layout="wide")
st.title("📄 DOC AI — Extract Structured Legal Info from Scanned PDFs")

uploaded_pdf = st.file_uploader("📤 Upload a scanned legal PDF", type=["pdf"])

if uploaded_pdf:
    with st.spinner("🔍 Extracting text from PDF using Google Vision..."):
        try:
            extracted_text = extract_text_from_pdf(uploaded_pdf)
        except Exception as e:
            st.error(f"❌ Failed to extract text: {e}")
            st.stop()

    st.success("✅ Text extracted from PDF!")
    st.subheader("📃 Raw OCR Text")
    st.text_area("OCR Output", extracted_text, height=300)

    if st.button("🔍 Extract Structured Legal Info using LLaMA"):
        prompt = f"""
You are a legal assistant AI. Based on the OCR text below, extract the following structured fields:

- Document Type (e.g., Sale Deed, Lease, Agreement)
- Document Date
- Buyer and Seller Names
- Property Address, Plot Number, Area
- Witnesses or Signatories
- Registration Number or Stamp ID (if any)

OCR TEXT:
{extracted_text}
"""
        with st.spinner("🦙 Asking LLaMA..."):
            structured = ask_llama(prompt)
            st.subheader("🧾 LLaMA Structured Output")
            st.text_area("Structured Info", structured, height=400)
