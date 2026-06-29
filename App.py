import streamlit as st
import json
import re
from datetime import datetime
from google import genai
from google.genai import types
from fpdf import FPDF

# ═══════════════════════════════════════════════════════════
# CONFIGURARE ȘI PERSISTENȚĂ
# ═══════════════════════════════════════════════════════════
# Citim cheia din Secrets. Dacă nu există, va returna o eroare vizibilă.
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = None

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
    pdf.cell(200, 10, txt=f"Verdict: {data.get('verdict', 'N/A')}", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=f"Sumar: {data.get('sumar', 'Fără sumar')}")
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

st.title("🔍 Veritas Pro Max v3.4")

if not API_KEY:
    st.error("API Key negăsit. Verifică secțiunea Secrets din Streamlit Cloud (Format: GEMINI_API_KEY = 'AIza...')")
else:
    metoda = st.radio("Metodă analiză:", ["URL", "Text Simplu"])
    input_data = st.text_input("Introdu URL sau Text:")

    if st.button("Analizează"):
        if not input_data:
            st.warning("Te rog să introduci ceva de analizat.")
        else:
            with st.status("Analiză în curs...", expanded=True) as status:
                try:
                    client = genai.Client(api_key=API_KEY)
                    # Folosim gemini-1.5-flash pentru stabilitate maximă
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=f"Analizează următorul conținut pentru dezinformare. Răspunde strict în format JSON cu cheile 'verdict' și 'sumar': {input_data}",
                        config=types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    data = parse_json_safe(response.text)
                    
                    st.markdown(f"### Verdict: {data.get('verdict')}")
                    st.write(data.get('sumar'))
                    
                    pdf_bytes = genereaza_pdf(data, "Raport Veritas")
                    st.download_button("📥 Descarcă PDF", pdf_bytes, "raport.pdf", "application/pdf")
                    status.update(label="Analiză finalizată!", state="complete")
                    
                except Exception as e:
                    st.error(f"Eroare procesare: {e}")
