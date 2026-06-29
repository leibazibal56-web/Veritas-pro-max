import streamlit as st
import google.generativeai as genai
import json
import re
from fpdf import FPDF

# Configurare
st.set_page_config(page_title="Veritas Pro Max", layout="centered")
api_key = st.secrets.get("GEMINI_API_KEY")

st.title("🔍 Veritas Pro Max v3.7")

if not api_key:
    st.error("Lipsă API Key. Configurează 'GEMINI_API_KEY' în Secrets.")
else:
    # Configurare generativă
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    input_data = st.text_input("Introdu URL sau Text:")
    if st.button("Analizează"):
        with st.status("Analiză în curs...", expanded=True):
            try:
                # Generare conținut
                response = model.generate_content(
                    f"Analizează veridicitatea: {input_data}. Răspunde în format JSON cu cheile 'verdict' și 'sumar'."
                )
                
                # Parsare
                text = response.text
                match = re.search(r'\{.*\}', text, re.DOTALL)
                data = json.loads(match.group(0)) if match else {"verdict": "Eroare", "sumar": text}
                
                st.subheader(f"Verdict: {data.get('verdict')}")
                st.write(data.get('sumar'))
                
            except Exception as e:
                st.error(f"Eroare: {str(e)}")
