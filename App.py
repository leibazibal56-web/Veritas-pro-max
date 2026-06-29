import streamlit as st
import google.generativeai as genai
import json
import re

# Configurare pagină
st.set_page_config(page_title="Veritas Pro Max", layout="centered")

# Preluare cheie din Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

st.title("🔍 Veritas Pro Max v3.8")

if not api_key:
    st.error("Lipsă API Key în Secrets.")
else:
    # CONFIGURARE FORȚATĂ A VERSIUNII API
    # Folosim versiunea 'v1' pentru a evita eroarea v1beta
    genai.configure(api_key=api_key, transport='rest') 
    
    # Încercăm să apelăm modelul folosind clasa de bază
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    input_data = st.text_input("Introdu URL sau Text:")
    if st.button("Analizează"):
        with st.status("Analiză în curs...", expanded=True):
            try:
                response = model.generate_content(
                    f"Analizează veridicitatea: {input_data}. Răspunde în format JSON cu 'verdict' și 'sumar'."
                )
                
                text = response.text
                match = re.search(r'\{.*\}', text, re.DOTALL)
                data = json.loads(match.group(0)) if match else {"verdict": "Eroare", "sumar": text}
                
                st.subheader(f"Verdict: {data.get('verdict')}")
                st.write(data.get('sumar'))
                
            except Exception as e:
                st.error(f"Eroare: {str(e)}")
