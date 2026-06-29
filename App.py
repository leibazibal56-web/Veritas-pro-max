import streamlit as st
import requests
import json
import re
from fpdf import FPDF

st.set_page_config(page_title="Veritas Pro Max", layout="centered")
API_KEY = st.secrets.get("GEMINI_API_KEY")

st.title("🔍 Veritas Pro Max v3.9")

if not API_KEY:
    st.error("Lipsă API Key.")
else:
    input_data = st.text_input("Introdu URL sau Text:")
    
    if st.button("Analizează"):
        with st.status("Analiză în curs...", expanded=True):
            try:
                # URL-ul complet pentru versiunea V1 (nu V1BETA)
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                
                payload = {
                    "contents": [{"parts": [{"text": f"Analizează veridicitatea: {input_data}. Răspunde în format JSON cu 'verdict' și 'sumar'."}]}]
                }
                
                response = requests.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # Parsare
                    match = re.search(r'\{.*\}', text, re.DOTALL)
                    data = json.loads(match.group(0)) if match else {"verdict": "Eroare", "sumar": text}
                    
                    st.subheader(f"Verdict: {data.get('verdict')}")
                    st.write(data.get('sumar'))
                else:
                    st.error(f"Eroare API {response.status_code}: {response.text}")
                    
            except Exception as e:
                st.error(f"Eroare: {str(e)}")
