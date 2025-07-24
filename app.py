import streamlit as st
import os
from google.oauth2 import service_account
from google.cloud import vision_v1 as vision
from pdf2image import convert_from_bytes
import tempfile
from PIL import Image

st.set_page_config(page_title="DocAI OCR", page_icon="📄")
st.title("📄 Document OCR & Analysis")

# Upload PDF
uploaded_file = st.file_uploader("Upload a scanned legal PDF", type=["pdf"])

# Extract text from PDF using Google Cloud Vision API
def extract_text_from_pdf(pdf_bytes):
    try:
        creds = service_account.Credentials.from_service_account_info(st.secrets["GCP_CREDENTIALS"])
        client = vision.ImageAnnotatorClient(credentials=creds
{
  "type": "service_account",
  "project_id": "docai-ocr-466903",
  "private_key_id": "98a926bb3fe8f73b7f7dffbc424d190142eeaa59",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDpfgGIrRAhVSpd\nKijxlrE4f1aezQeXctQuAwrH0e+WR/iVDOOdyOtkkZ7oJjM0n10Uinf/Is+FtF6b\npUPKoZaWJdkEpnoNs1WD1yaJZKHgf0JxfILZfg+Dfng/07fQEirDnMc7IBTS/Ti+\nyWHsEAeinQ1gSV4+Qp3cduyvw7DAFz+o+vT7fGtv4IJpQeWZN2T8qDfsF3gVaISV\nCFcbD1lC8JiXE2C7qIf8b3UkDxNHFYGNRDKDDNrdhvmEen9MliyIARQr6kD7Eh/x\nmc3/Iqj+N7zw+Q5qe+Nbh+6b7h6W72N3satCxMRaUH8+mnHnQBcjiiwIjl8UjWLN\nYdl5pHaDAgMBAAECggEAB88Qa0TDP4ojBfigY+wGEBcNWF3dCiI4ZgC+CvUpDeqc\nR3sMRb08rVSQoiaQG3HU+0t71eTEWGFlSwLmihyIKVj2S0lSCneovX8KXLMor5X+\nxkYQWwiNqXhaU/zw4c/2h18MuE9LXJirBCs+z7x9ga4k9Ppr+ql5sONDtfq8ESbl\niLHegEG9z1l6nJTgzgDMH5ReGlW5+TvCTtpZP1bdyR5NW5m5uKmPhqDtWn4mlfUV\nGDfzM3nivaAeorclifTGZKRXdRE7gmexUIblUTxyZDTrH0pQmKvl542maTpJMDPt\nBT1BiYNzT6W/o6NHDRmiV0wNXPfsFjGSwT+U9iTPAQKBgQD84gcsFJaxS6hHanxZ\n2QOflVZ7ZSxE1KnGx6XF7ib5nnZ43C++yvzdc2glTGQ6uHxhTaKvgLMP8t8k94Fp\npBauTlGeGyi4D+6DTOp54OLRKHG7QOw287o6VSvtNo57SbjkWj9Gw7+Y6SSxRH7S\n8JHSrRdP6bLnTAdfbIO9e/nCgQKBgQDsXspkRs7HrfZEVQFrLYCiKAbnxwO9Go9H\n+V1qjSj+3VkPmYuHT7ZF2xXYAR5rx/w2T9Bkf4yTKstmbbJAWQ+47TCPJx/LWXGe\noGio+Al1Ug7fxKwrL98wmV4unInA9UvwKDrqcd69berIvvh6OKOKXPy+5SARtfgD\n19K1Z0GvAwKBgQD0y5SnzjJl5Fg88c74ZsREKhsyjijBZKAIxeEqbjSadRQ4QOWT\nKwqHEJ2jZYSs90OoKbAvdkVgTfpG3bUP34D5MOV/SMktDHcV8VIVs2W9lQore1hu\nhZcjuqkwExzwKdhqbRZN2VXSnvYfB7BBYBG5QEeN2yuNDaMhc3k/5xBKgQKBgQDk\nGLlAuV/UK5jp6gobbmailPPM+S0vcJDyCL7QEvaLs/i86BRQeGjR0pCqyLGdmvhV\nRQI56Sgz4Gk2KAeKtydH8oQYsM2qw160j+FPpUQjVhOKdtUaO/EqieXsHx2D+nLU\nh04LbeVfcdHO9RL9huiynfc9FAi1bp+uvbfVXJZzFwKBgQCYTxnoWdr+CPLh/iFi\nBwut82yFtlwrIpXr9bSxLPc8f4MdwynvI069AaIaKvhJKLAEhd1EjbaOH9ZufDwf\nOKrUTmGF8vykxFqKicAaIRLjY4Twp4P/2y364cMy+hvAU5kE/f6FYQDhbPy1NjfF\nvc31kFHdwhxy2s5OhNs6I/g/lQ==\n-----END PRIVATE KEY-----\n",
  "client_email": "docai-vision-user@docai-ocr-466903.iam.gserviceaccount.com",
  "client_id": "110824803886006875525",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/docai-vision-user%40docai-ocr-466903.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

        # Convert PDF pages to images
        images = convert_from_bytes(pdf_bytes)
        all_text = ""

        for idx, img in enumerate(images):
            st.image(img, caption=f"📄 Page {idx + 1}", use_column_width=True)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                img.save(tmp.name, format='PNG')
                with open(tmp.name, 'rb') as f:
                    image = vision.Image(content=f.read())
                    response = client.document_text_detection(image=image)

                    if response.error.message:
                        st.error(f"❌ Vision API error: {response.error.message}")
                        return ""

                    annotation = response.full_text_annotation.text
                    if not annotation.strip():
                        st.warning(f"⚠️ No text detected on Page {idx + 1}. Try a clearer scan.")
                    else:
                        all_text += annotation + "\n"

                os.remove(tmp.name)

        if not all_text.strip():
            st.error("❌ No text detected on any page. Try a clearer PDF.")
            return None

        return all_text

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
