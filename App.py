import streamlit as st
import json
import requests
import re
import os
from datetime import datetime
from google import genai
from google.genai import types
from fpdf import FPDF

# ═══════════════════════════════════════════════════════════
# CONFIGURARE ȘI PERSISTENȚĂ
# ═══════════════════════════════════════════════════════════
# Verificăm cheia din environment sau secrets
API_KEY = st.secrets.get("GEMINI_API_KEY")

def genereaza_pdf(data, titlu):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="RAPORT FACT-CHECKING VERITAS", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Data: {datetime.now().strftime('%d.%m.%Y')}", ln=True)
    pdf.cell(200, 10, txt=f"Sursa: {titlu}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Verdict: {data.get('verdict')}", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=f"Sumar: {data.get('sumar')}")
    return pdf.output(dest='S').encode('latin-1')

def parse_json_safe(raw_text):
    match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    if match: return json.loads(match.group(0))
    raise ValueError("Eroare parsare JSON.")

# ═══════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════
st.set_page_config(page_title="Veritas Pro Max", layout="centered")
st.markdown("<style>.stApp { background: #080D1A; color: #C8D8F0; }</style>", unsafe_allow_html=True)

st.title("🔍 Veritas Pro Max v3.3")

if not API_KEY:
    st.error("Eroare de configurare: API Key-ul nu a fost găsit. Te rugăm să verifici secțiunea Secrets din Streamlit Cloud.")
else:
    metoda = st.radio("Metodă analiză:", ["URL", "Imagine"])
    input_data = st.text_input("URL:") if metoda == "URL" else st.file_uploader("Încarcă imagine:")

    if st.button("Analizează"):
        with st.status("Analiză în curs...", expanded=True) as status:
            try:
                client = genai.Client(api_key=API_KEY)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents="Analizează contextul politic 2026 (Nicușor Dan Președinte). Răspunde JSON.",
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                data = parse_json_safe(response.text)
                
                st.markdown(f"### Verdict: {data['verdict']}")
                st.write(data['sumar'])
                
                pdf_bytes = genereaza_pdf(data, "Raport Veritas")
                st.download_button("📥 Descarcă PDF", pdf_bytes, "raport.pdf", "application/pdf")
            except Exception as e:
                st.error(f"Eroare procesare: {e}")
