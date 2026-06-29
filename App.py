import streamlit as st
import json
import requests
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# CONFIGURARE ȘI UI
# ═══════════════════════════════════════════════════════════
st.set_page_config(page_title="Veritas Pro Max", page_icon="🔍", layout="centered")

st.title("🔍 VERITAS PRO MAX v4.5")
API_KEY = st.secrets.get("GEMINI_API_KEY")

# ═══════════════════════════════════════════════════════════
# LOGICA API
# ═══════════════════════════════════════════════════════════
def apeleaza_gemini(continut_text):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-002:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": continut_text}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 429:
        raise Exception("429_LIMIT")
    
    if response.status_code != 200:
        raise Exception(f"Eroare API {response.status_code}: {response.text}")
        
    return json.loads(response.json()['candidates'][0]['content']['parts'][0]['text'])

# ═══════════════════════════════════════════════════════════
# EXECUȚIE
# ═══════════════════════════════════════════════════════════
input_user = st.text_input("Introdu text sau URL pentru analiză:")

if st.button("Analizează"):
    if not API_KEY:
        st.error("Configurează cheia API în Secrets.")
    elif not input_user:
        st.warning("Introdu date pentru analiză.")
    else:
        with st.status("Analiză în curs...", expanded=True):
            try:
                # Prompt-ul definit pe o singură linie pentru siguranță
                prompt = f"Data: {datetime.now().strftime('%d.%m.%Y')}. Analizează veridicitatea: {input_user}. Răspunde strict în format JSON cu cheile: 'scor' (int), 'verdict' (string), 'sumar' (string), 'recomandari' (string)."
                
                rezultat = apeleaza_gemini(prompt)
                
                st.subheader(f"Verdict: {rezultat.get('verdict')} ({rezultat.get('scor')}/100)")
                st.write(f"**Sumar:** {rezultat.get('sumar')}")
                st.info(f"**Recomandare:** {rezultat.get('recomandari')}")
                
            except Exception as e:
                if "429_LIMIT" in str(e):
                    st.error("⚠️ Limita gratuită de cereri a fost atinsă. Așteaptă 1 minut.")
                else:
                    st.error(f"Eroare: {str(e)}")
