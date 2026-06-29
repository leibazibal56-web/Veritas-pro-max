import streamlit as st
import json
import requests
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# CONFIGURARE ȘI INTERFAȚĂ
# ═══════════════════════════════════════════════════════════
st.set_page_config(page_title="Veritas Pro Max", page_icon="🔍", layout="centered")
st.title("🔍 VERITAS PRO MAX v5.0")

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ═══════════════════════════════════════════════════════════
# LOGICĂ API (Cea mai stabilă metodă)
# ═══════════════════════════════════════════════════════════
def apeleaza_gemini(continut_text):
    # Folosim calea generică pentru modelul 1.5-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": continut_text}]}]
    }
    
    response = requests.post(url, json=payload)
    
    # Gestionare erori
    if response.status_code == 429:
        raise Exception("429_LIMIT")
    if response.status_code != 200:
        raise Exception(f"Eroare {response.status_code}: {response.text}")
        
    # Extragere text
    raw_text = response.json()['candidates'][0]['content']['parts'][0]['text']
    # Curățare format pentru a asigura JSON pur
    clean_text = raw_text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_text)

# ═══════════════════════════════════════════════════════════
# EXECUȚIE ȘI UI
# ═══════════════════════════════════════════════════════════
input_user = st.text_input("Introdu URL sau text pentru analiză:")

if st.button("Analizează"):
    if not API_KEY:
        st.error("Lipsă cheie API în Secrets.")
    elif not input_user:
        st.warning("Introdu ceva de verificat!")
    else:
        with st.status("Analiză Veritas în curs...", expanded=True):
            try:
                # Prompt instructiv pentru structură
                prompt = (f"Data: {datetime.now().strftime('%d.%m.%Y')}. "
                          f"Verifică: {input_user}. "
                          "Răspunde STRICT în format JSON (fără alte texte): "
                          "{'scor': int, 'verdict': string, 'sumar': string, 'recomandari': string}")
                
                rezultat = apeleaza_gemini(prompt)
                
                st.subheader(f"Verdict: {rezultat.get('verdict')} ({rezultat.get('scor')}/100)")
                st.write(f"**Sumar:** {rezultat.get('sumar')}")
                st.info(f"**Recomandare:** {rezultat.get('recomandari')}")
                
            except Exception as e:
                if "429_LIMIT" in str(e):
                    st.error("⚠️ Limită atinsă. Așteaptă 1 minut.")
                else:
                    st.error(f"Eroare: {str(e)}")
