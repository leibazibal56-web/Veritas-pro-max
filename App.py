import streamlit as st
import json
import requests
from urllib.parse import urlparse
from datetime import datetime
from bs4 import BeautifulSoup
from google import genai
from google.genai import types

# ═══════════════════════════════════════════════════════════
# CONFIGURARE PAGINĂ STREAMLIT
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Veritas Pro Max - Fact Checking",
    page_icon="🔍",
    layout="centered"
)

# Stiluri vizuale personalizate (Dark Mode Elegant)
st.markdown("""
    <style>
    .main { background-color: #0F1628; color: #F0F4FF; }
    h1 { color: #F0F4FF; text-align: center; font-family: sans-serif; }
    .stButton>button { width: 100%; background-color: #5B9BFF; color: white; border-radius: 8px; }
    .credibil-box { background: #0F1628; border-left: 5px solid #4FFFB0; padding: 20px; border-radius: 10px; margin: 15px 0; }
    .suspicios-box { background: #0F1628; border-left: 5px solid #FF6B35; padding: 20px; border-radius: 10px; margin: 15px 0; }
    .necredibil-box { background: #0F1628; border-left: 5px solid #FF3366; padding: 20px; border-radius: 10px; margin: 15px 0; }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 VERITAS PRO MAX")
st.caption("Platformă inteligentă pentru analiza credibilității știrilor în timp real")

# Initializează istoricul în sesiunea browserului
if "istoric_web" not in st.session_state:
    st.session_state.istoric_web = []

# ═══════════════════════════════════════════════════════════
# VERIFICARE AUTOMATĂ ÎN STREAMLIT SECRETS (CHEIA ASCUNSĂ)
# ═══════════════════════════════════════════════════════════
if "GEMINI_API_KEY" in st.secrets:
    user_api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.sidebar.header("🔑 Configurare Securitate")
    user_api_key = st.sidebar.text_input("Introdu Cheia API Gemini:", type="password", value="")

st.sidebar.markdown("""
---
### Despre Veritas Pro Max
Această platformă extrage textul din linkul trimis și folosește inteligența artificială **Gemini 2.5 Flash** calibrată la zi pentru a evalua corectitudinea factuală a știrilor.
""")

# ═══════════════════════════════════════════════════════════
# LOGICA TEHNICĂ
# ═══════════════════════════════════════════════════════════
def valideaza_url(url):
    if not url or not url.strip():
        return False, "Vă rugăm să introduceți un URL valid!"
    parsed = urlparse(url.strip())
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        return False, "URL-ul trebuie să fie o adresă web validă (https://...)."
    if parsed.hostname in {'localhost', '127.0.0.1', '0.0.0.0'}:
        return False, "Acces nepermis."
    return True, url.strip()

def extrage_continut(url):
    try:
        res = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        titlu = soup.title.string if soup.title else "Titlu necunoscut"
        text = " ".join([p.text for p in soup.find_all('p')[:10]])
        return titlu, text
    except Exception as e:
        raise Exception(f"Nu s-a putut accesa site-ul: {str(e)}")

# ═══════════════════════════════════════════════════════════
# INTERFAȚA PRINCIPALĂ
# ═══════════════════════════════════════════════════════════
url_tinta = st.text_input("Introdu URL-ul articolului pe care vrei să îl verifici:", placeholder="https://example.com/stire...")

if st.button("Analizează Articolul"):
    if not user_api_key:
        st.error("⚠️ Aplicația nu este configurată! Introduceți cheia API în bara laterală sau în setările Secrets.")
    else:
        este_valid, rezultat_url = valideaza_url(url_tinta)
        if not este_valid:
            st.error(rezultat_url)
        else:
            with st.spinner("⏳ Veritas AI analizează contextul contemporan..."):
                try:
                    titlu_articol, text_articol = extrage_continut(rezultat_url)
                    
                    # Conexiune Gemini securizată
                    client = genai.Client(api_key=user_api_key)
                    
                    # I-am dat contextul direct în text pentru a evita erorile de autentificare cu Google Search
                    prompt = (
                        "Ești un expert fact-checker. Răspunde STRICT în format JSON valid cu cheile: {scor: int, verdict: string, sumar: string, recomandari: string}. "
                        "Verdictul poate fi doar: CREDIBIL, SUSPICIOS sau NECREDIBIL. "
                        "NOTĂ FACTUALĂ IMPORTANTĂ PENTRU REALIATEA DIN 2026: Nicușor Dan este în prezent Președintele României, "
                        "iar pe scena politică există dispute privind formarea Guvernului și desemnarea unui nou premier interimar. "
                        "Evaluează textul articolului ținând cont de aceste date absolut reale pentru prezentul nostru."
                    )
                    msg = f"Analizează textul următor:\nTitlu: {titlu_articol}\nConținut: {text_articol[:2000]}"
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=msg,
                        config=types.GenerateContentConfig(system_instruction=prompt, response_mime_type="application/json")
                    )
                    
                    date_analiza = json.loads(response.text)
                    
                    # Salvare în istoric sesiune
                    st.session_state.istoric_web.insert(0, {
                        "data": datetime.now().strftime('%d.%m.%Y %H:%M'),
                        "titlu": titlu_articol,
                        "verdict": date_analiza['verdict'],
                        "scor": date_analiza['scor']
                    })
                    
                    # Afișare casetă rezultat în funcție de verdict
                    clasa_box = "necredibil-box"
                    if date_analiza['verbit'] == "CREDIBIL" or date_analiza['verdict'] == "CREDIBIL": clasa_box = "credibil-box"
                    elif date_analiza['verdict'] == "SUSPICIOS": clasa_box = "suspicios-box"
                    
                    st.markdown(f"""
                        <div class="{clasa_box}">
                            <h2 style='margin:0;'>Verdict: {date_analiza['verdict']} ({date_analiza['scor']}/100)</h2>
                            <p><strong>Titlu detectat:</strong> {titlu_articol}</p>
                            <p style='color: #CCD6E8;'>{date_analiza['sumar']}</p>
                            <p style='color: #8899BB; font-style: italic;'><strong>Recomandare:</strong> {date_analiza['recomandari']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Opțiune descărcare raport rapid text
                    raport_text = f"RAPORT VERITAS\nURL: {rezultat_url}\nVerdict: {date_analiza['verdict']} ({date_analiza['scor']}/100)\nSumar: {date_analiza['sumar']}"
                    st.download_button("📥 Descarcă Raport Text", data=raport_text, file_name="raport_veritas.txt")
                    
                except Exception as e:
                    st.error(f"❌ A apărut o eroare la analiză: {str(e)}")

# Afișare Istoric Sesiune în partea de jos
if st.session_state.istoric_web:
    st.write("---")
    st.subheader("📋 Istoricul căutărilor tale din această sesiune")
    for item in st.session_state.istoric_web:
        st.write(f"⏱️ **{item['data']}** | {item['titlu'][:60]}... -> **{item['verdict']}** ({item['scor']}/100)")
