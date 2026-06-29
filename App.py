import streamlit as st
import json
import requests
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# UI ȘI CONFIGURARE
# ═══════════════════════════════════════════════════════════
st.set_page_config(page_title="Veritas Pro Max", page_icon="🔍", layout="centered")
st.title("🔍 VERITAS PRO MAX v5.2")
API_KEY = st.secrets.get("GEMINI_API_KEY")

# ═══════════════════════════════════════════════════════════
# LOGICĂ API CU REDUNDANȚĂ (Previne eroarea 404)
# ═══════════════════════════════════════════════════════════
def apeleaza_gemini(continut_de_verificat):
    # Payload-ul standard
    payload = {"contents": [{"parts": [{"text": continut_de_verificat}]}]}
    
    # Încercăm două variante de endpoint pentru a evita 404
    urls = [
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}",
        f"https://generativelanguage.googleapis.com/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    ]
    
    response = None
    for url in urls:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            break
    
    # Gestionare erori
    if response.status_code == 429:
        raise Exception("429_LIMIT")
    if response.status_code != 200:
        raise Exception(f"Eroare API {response.status_code}: {response.text}")
        
    # Extragere și curățare
    raw_text = response.json()['candidates'][0]['content']['parts'][0]['text']
    clean_text = raw_text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_text)

# ═══════════════════════════════════════════════════════════
# EXECUȚIE
# ═══════════════════════════════════════════════════════════
input_user = st.text_input("Introdu URL sau text pentru analiză:")

if st.button("Analizează"):
    if not API_KEY:
        st.error("Lipsă cheie API în Secrets.")
    elif not input_user:
        st.warning("Introdu ceva de verificat!")
    else:
        with st.spinner("Veritas Pro analizează sursa..."):
            try:
                prompt = (f"Data curentă: {datetime.now().strftime('%d.%m.%Y')}. "
                          f"Verifică: {input_user}. "
                          "Răspunde STRICT în format JSON: "
                          "{'scor': int, 'verdict': string, 'sumar': string, 'recomandari': string}")
                
                rezultat = apeleaza_gemini(prompt)
                
                st.subheader(f"Verdict: {rezultat.get('verdict')} ({rezultat.get('scor')}/100)")
                st.write(f"**Sumar:** {rezultat.get('sumar')}")
                st.info(f"**Recomandare:** {rezultat.get('recomandari')}")
                
            except Exception as e:
                st.error(f"Eroare: {str(e)}")
