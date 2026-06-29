import streamlit as st
import requests
import json
import re
from datetime import datetime
from fpdf import FPDF

# ═══════════════════════════════════════════════════════════
# CONFIGURARE ȘI FUNCȚII AUXILIARE
# ═══════════════════════════════════════════════════════════
st.set_page_config(page_title="Veritas Pro Max", layout="centered")
API_KEY = st.secrets.get("GEMINI_API_KEY")

def genereaza_pdf(data, titlu):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="RAPORT FACT-CHECKING VERITAS", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Data: {datetime.now().strftime('%d.%m.%Y')}", ln=True)
    pdf.cell(200, 10, txt=f"Sursa: {titlu[:50]}...", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Verdict: {data.get('verdict', 'N/A')}", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=f"Sumar: {data.get('sumar', 'Fără sumar')}")
    return pdf.output(dest='S').encode('latin-1')

# ═══════════════════════════════════════════════════════════
# UI ȘI LOGICĂ PRINCIPALĂ
# ═══════════════════════════════════════════════════════════
st.title("🔍 Veritas Pro Max v4.1")

if not API_KEY:
    st.error("Lipsă API Key. Configurează 'GEMINI_API_KEY' în Secrets.")
else:
    input_data = st.text_input("Introdu URL sau Text:")
    
    if st.button("Analizează"):
        if not input_data:
            st.warning("Te rog introdu un text sau URL.")
        else:
            with st.status("Analiză în curs cu Gemini 1.5 Flash...", expanded=True):
                try:
                    # Folosim modelul gemini-1.5-flash
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                    
                    payload = {
                        "contents": [{
                            "parts": [{"text": f"Analizează veridicitatea acestui conținut: {input_data}. Răspunde strict în format JSON cu cheile 'verdict' (Adevărat/Fals/Înșelător) și 'sumar'."}]
                        }]
                    }
                    
                    response = requests.post(url, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        raw_text = result['candidates'][0]['content']['parts'][0]['text']
                        
                        # Parsare JSON
                        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                        data = json.loads(match.group(0)) if match else {"verdict": "Eroare", "sumar": raw_text}
                        
                        st.subheader(f"Verdict: {data.get('verdict')}")
                        st.write(data.get('sumar'))
                        
                        # PDF
                        pdf_bytes = genereaza_pdf(data, input_data)
                        st.download_button("📥 Descarcă Raport PDF", pdf_bytes, "raport.pdf", "application/pdf")
                    else:
                        st.error(f"Eroare API {response.status_code}: {response.text}")
                        
                except Exception as e:
                    st.error(f"Eroare procesare: {str(e)}")
