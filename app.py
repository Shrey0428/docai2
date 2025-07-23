import streamlit as st
from google.cloud import vision
from google.oauth2 import service_account
import tempfile
import subprocess

# === Configure Google Vision credentials ===
CREDENTIALS_PATH = "service_account.json"

# === Ask LLaMA using Ollama (local) ===
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
        return f"❌ Error running LLaMA: {e}"

# === Use Google Cloud Vision API to extract text from PDF ===
def extract_text_from_pdf(pdf_file):
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(pdf_file.read())
        temp_path = temp_file.name

    # Setup Vision client
    creds = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
    client = vision.ImageAnnotatorClient(credentials=creds)

    # Read PDF into bytes
    with open(temp_path, 'rb') as f:
        pdf_content = f.read()

    # Vision request
    mime_type = 'application/pdf'
    input_config = vision.types.InputConfig(content=pdf_content, mime_type=mime_type)
    features = [{"type_": vision.Feature.Type.DOCUMENT_TEXT_DETECTION}]
    request = vision.AnnotateFileRequest(input_config=input_config, features=features)

    response = client.batch_annotate_files(requests=[request])
    all_text = ""
    for page in response.responses[0].responses:
        if page.full_text_annotation.text:
            all_text += page.full_text_annotation.text + "\n"
    return all_text

# === Streamlit UI ===
st.set_page_config(page_title="DOCAI", layout="wide")
st.title("📄 DOC AI: Extract Legal Info from Scanned PDF")

uploaded_pdf = st.file_uploader("Upload Scanned Legal PDF", type=["pdf"])

if uploaded_pdf:
    with st.spinner("🔍 Extracting text from PDF using Google Vision..."):
        try:
            extracted_text = extract_text_from_pdf(uploaded_pdf)
        except Exception as e:
            st.error(f"❌ Failed to extract text: {e}")
            st.stop()

    st.success("✅ Text extracted successfully!")
    st.subheader("📃 OCR Text")
    st.text_area("Raw OCR Output", extracted_text, height=300)

    # Ask LLaMA to extract structure
    if st.button("🔍 Extract Structured Fields using LLaMA"):
        prompt = f"""
You are a legal assistant AI. Based on the OCR text below, extract the following:

- Document Type (e.g., Sale Deed, Lease, Agreement)
- Date of Document
- Parties Involved (Buyer, Seller, Authority)
- Property Address, Plot Number, Area
- Witness Names or Signatories
- Any Registration Number or Stamp ID

OCR TEXT:
{extracted_text}
"""
        with st.spinner("🦙 Talking to LLaMA..."):
            structured = ask_llama(prompt)
            st.subheader("🧾 Structured Data")
            st.text_area("LLaMA Output", structured, height=400)
