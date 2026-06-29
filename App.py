import streamlit as st
import json
import re
from datetime import datetime
from google import genai
from fpdf import FPDF

# ═══════════════════════════════════════════════════════════
# UI și Logică
# ═══════════════════════════════════════════════════════════
st.set_page_config(page_title="Veritas Pro Max", layout="centered")
API_KEY = st.secrets.get("GEMINI_API_KEY")

st.title("🔍 Veritas Pro Max v3.6")

if not API_KEY:
    st.error("Lipsă API Key. Configurează 'GEMINI_API_KEY' în Secrets.")
else:
    input_data = st.text_input("Introdu URL sau Text:")
    if st.button("Analizează"):
        with st.status("Analiză în curs...", expanded=True):
            try:
                # Inițializare client
                client = genai.Client(api_key=API_KEY)
                
                # Apel direct pe modelul de bază
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=f"Analizează veridicitatea: {input_data}. Răspunde în format JSON cu 'verdict' și 'sumar'."
                )
                
                # Parsare
                raw_text = response.text
                match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                data = json.loads(match.group(0)) if match else json.loads(raw_text)
                
                st.subheader(f"Verdict: {data.get('verdict')}")
                st.write(data.get('sumar'))
                
            except Exception as e:
                st.error(f"Eroare: {str(e)}")
