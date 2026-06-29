import streamlit as st
import requests
import json
import re
from fpdf import FPDF

# Configurare pagină
st.set_page_config(page_title="Veritas Pro Max", layout="centered")

# Preluare cheie din Secrets
API_KEY = st.secrets.get("GEMINI_API_KEY")

st.title("🔍 Veritas Pro Max v4.0")

if not API_KEY:
    st.error("Lipsă API Key. Configurează 'GEMINI_API_KEY' în Secrets.")
else:
    input_data = st.text_input("Introdu URL sau Text:")
    
    if st.button("Analizează"):
        if not input_data:
            st.warning("Te rog introdu un text sau URL.")
        else:
            with st.status("Analiză în curs cu Gemini...", expanded=True):
                try:
                    # Endpoint-ul corect pentru modelele 1.5
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
                    else:
                        st.error(f"Eroare API {response.status_code}: {response.text}")
                        
                except Exception as e:
                    st.error(f"Eroare procesare: {str(e)}")
