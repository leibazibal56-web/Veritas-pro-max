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
# Citim cheia din Secrets.
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
    # Caută conținutul JSON în text, chiar dacă API-ul mai adaugă text informativ
    match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    if match: 
        return json.loads(match.group(0))
    else:
        # Încearcă să parșezi tot textul dacă nu găsește blocul { }
        return json.loads(raw_text)

# ═══════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════
st.set_page_config(page_title="Veritas Pro Max", layout="centered")
st.markdown("<style>.stApp { background: #080D1A; color: #C8D8F0; }</style>", unsafe_allow_html=True)

st.title("🔍 Veritas Pro Max v3.5")

if not API_KEY:
    st.error("Eroare: Cheia API nu a fost detectată. Verifică secțiunea 'Secrets' din dashboard-ul Streamlit.")
else:
    input_data = st.text_input("Introdu URL sau Text de analizat:")

    if st.button("Analizează"):
        if not input_data:
            st.warning("Te rog să introduci un URL sau un text.")
        else:
            with st.status("Analiză în curs cu Gemini...", expanded=True) as status:
                try:
                    client = genai.Client(api_key=API_KEY)
                    
                    # Utilizăm modelul stabil 1.5-flash-002
                    response = client.models.generate_content(
                        model='gemini-1.5-flash-002',
                        contents=f"Analizează următorul conținut și verifică veridicitatea. Răspunde strict în format JSON cu cheile 'verdict' (ex: Adevărat/Fals/Înșelător) și 'sumar': {input_data}",
                        config=types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    
                    data = parse_json_safe(response.text)
                    
                    st.markdown(f"### Verdict: {data.get('verdict')}")
                    st.write(data.get('sumar'))
                    
                    pdf_bytes = genereaza_pdf(data, input_data[:30] + "...")
                    st.download_button("📥 Descarcă Raport PDF", pdf_bytes, "raport_veritas.pdf", "application/pdf")
                    
                    status.update(label="Analiză finalizată cu succes!", state="complete")
                    
                except Exception as e:
                    st.error(f"Eroare procesare: {str(e)}")
