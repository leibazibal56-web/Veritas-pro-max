import streamlit as st
import json
import requests
import random
import time
import re
import os
from urllib.parse import urlparse
from datetime import datetime
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from PIL import Image
from fpdf import FPDF

# ═══════════════════════════════════════════════════════════
# CONFIGURARE ȘI PERSISTENȚĂ
# ═══════════════════════════════════════════════════════════
HISTORIC_FILE = "istoric_analize.json"

def incarca_istoric():
    if os.path.exists(HISTORIC_FILE):
        try:
            with open(HISTORIC_FILE, "r") as f: return json.load(f)
        except: return []
    return []

def salveaza_istoric(istoric):
    with open(HISTORIC_FILE, "w") as f: json.dump(istoric, f)

# ═══════════════════════════════════════════════════════════
# GENERARE PDF
# ═══════════════════════════════════════════════════════════
def genereaza_pdf(data, titlu):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="RAPORT FACT-CHECKING VERITAS", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Data: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=True)
    pdf.cell(200, 10, txt=f"Sursa: {titlu}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Verdict: {data.get('verdict')}", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=f"Sumar: {data.get('sumar')}")
    return pdf.output(dest='S').encode('latin-1')

# ═══════════════════════════════════════════════════════════
# PARSARE ȘI UI
# ═══════════════════════════════════════════════════════════
def parse_json_safe(raw_text):
    match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    if match: return json.loads(match.group(0))
    raise ValueError("Eroare parsare JSON.")

st.set_page_config(page_title="Veritas Pro Max", layout="centered")
st.markdown("<style>.stApp { background: #080D1A; color: #C8D8F0; }</style>", unsafe_allow_html=True)

st.title("🔍 Veritas Pro Max v3.2")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
istoric = incarca_istoric()

metoda = st.radio("Metodă analiză:", ["URL", "Imagine"])
input_data = st.text_input("URL:") if metoda == "URL" else st.file_uploader("Încarcă imagine:")

if st.button("Analizează"):
    if not api_key: st.error("Introdu API Key!")
    else:
        with st.status("Analiză în curs...", expanded=True) as status:
            try:
                client = genai.Client(api_key=api_key)
                # (Aici se adaugă logica de prompt fix din v3.0 pentru context 2026)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents="Analizează acest conținut conform contextului politic 2026 (Nicușor Dan Președinte). Răspunde JSON.",
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                data = parse_json_safe(response.text)
                
                # Salvare și Afișare
                istoric.insert(0, {"data": datetime.now().isoformat(), "titlu": "Analiză", "verdict": data.get("verdict")})
                salveaza_istoric(istoric)
                
                st.markdown(f"### Verdict: {data['verdict']}")
                st.write(data['sumar'])
                
                # Butoane Export
                pdf_bytes = genereaza_pdf(data, "Raport")
                st.download_button("📥 Descarcă PDF", pdf_bytes, "raport.pdf", "application/pdf")
                
            except Exception as e: st.error(f"Eroare: {e}")

# Istoric Sidebar
st.sidebar.subheader("Istoric Sesiuni")
for h in istoric[:5]:
    st.sidebar.write(f"{h['verdict']} | {h['data'][:10]}")
