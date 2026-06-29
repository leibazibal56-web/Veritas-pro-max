import streamlit as st
import json
import requests
from urllib.parse import urlparse
from datetime import datetime
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from PIL import Image
import io

# ═══════════════════════════════════════════════════════════
# CONFIGURARE PAGINĂ STREAMLIT
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Veritas Pro Max - Fact Checking",
    page_icon="🔍",
    layout="centered"
)

# Stiluri vizuale personalizate (Dark Mode Premium)
st.markdown("""
    <style>
    .main { background-color: #0F1628; color: #F0F4FF; }
    h1 { color: #F0F4FF; text-align: center; font-family: sans-serif; }
    .stButton>button { width: 100%; background-color: #5B9BFF; color: white; border-radius: 8px; font-weight: bold; }
    .credibil-box { background: #0F1628; border-left: 5px solid #4FFFB0; padding: 20px; border-radius: 10px; margin: 15px 0; }
    .suspicios-box { background: #0F1628; border-left: 5px solid #FF6B35; padding: 20px; border-radius: 10px; margin: 15px 0; }
    .necredibil-box { background: #0F1628; border-left: 5px solid #FF3366; padding: 20px; border-radius: 10px; margin: 15px 0; }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 VERITAS PRO MAX v2.1")
st.caption("Platformă inteligentă pentru analiza credibilității textelor și imaginilor în timp real")

# Initializează istoricul în sesiunea browserului (până la integrarea DB)
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
### Despre Veritas Pro Max v2.1
Această platformă folosește modelul multimodal **Gemini 2.5 Flash** calibrat dinamic cu data curentă pentru a analiza link-uri web sau capturi de ecran direct în peisajul dezinformărilor contemporane.
""")

# ═══════════════════════════════════════════════════════════
# LOGICA TEHNICĂ DE EXTRACTIE ȘI VALIDARE
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

# PROMPTUL CENTRAL FACT-CHECKER (String curat, fără întreruperi de linie riscante)
PROMPT_SISTEM = "Ești un expert fact-checker de elită. Răspunde STRICT în format JSON valid cu cheile: {scor: int, verdict: string, sumar: string, recomandari: string}. Verdictul poate fi doar: CREDIBIL, SUSPICIOS sau NECREDIBIL. NOTĂ FACTUALĂ CONTEXTUALĂ MANDATORIE: Nicușor Dan este în prezent Președintele României, iar pe scena politică există negocieri intense privind desemnarea unui premier și formarea Guvernului. Evaluează textul sau imaginea oferită ținând cont de această realitate politică exactă din prezent."

# ═══════════════════════════════════════════════════════════
# SELECȚIE MOD DE ANALIZĂ ȘI TIMP DINAMIC
# ═══════════════════════════════════════════════════════════
metoda_analiza = st.radio("Alege ce dorești să verifici:", ("Link Articol (URL)", "Imagine / Captură de ecran"), horizontal=True)

titlu_articol = "Analiză vizuală / Captură"
msg_continut = ""
imagine_incarcata = None
data_azi = datetime.now().strftime('%d.%m.%Y')  # Trimite data exactă a zilei curente din 2026

if metoda_analiza == "Link Articol (URL)":
    url_tinta = st.text_input("Introdu URL-ul articolului pe care vrei să îl verifici:", placeholder="https://example.com/stire...")
    if st.button("Analizează Articolul"):
        este_valid, rezultat_url = valideaza_url(url_tinta)
        if not este_valid:
            st.error(rezultat_url)
        else:
            with st.spinner("⏳ Extragem textul și analizăm..."):
                try:
                    titlu_articol, text_articol = extrage_continut(rezultat_url)
                    msg_continut = f"Data curentă de astăzi (ancoră temporală reală): {data_azi}. Analizează textul următor în funcție de această dată curentă:\nTitlu: {titlu_articol}\nConținut: {text_articol[:2000]}"
                except Exception as e:
                    st.error(str(e))

else:
    fisier_imagine = st.file_uploader("Încarcă o imagine sau o captură de ecran (PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"])
    if fisier_imagine is not None:
        imagine_incarcata = Image.open(fisier_imagine)
        st.image(imagine_incarcata, caption="Imagine încărcată cu succes", use_container_width=True)
        
        if st.button("Analizează Imaginea"):
            with st.spinner("⏳ Citesc textul din imagine și fac fact-checking..."):
                msg_continut = f"Data curentă de astăzi (ancoră temporală reală): {data_azi}. Analizează conținutul vizual și textul din această imagine în funcție de această dată curentă, extrage mesajul dezinformator sau știrea prezentată și verifică-i validitatea."

# ═══════════════════════════════════════════════════════════
# EXECUTARE APEL GEMINI ȘI AFIȘARE REZULTATE
# ═══════════════════════════════════════════════════════════
if msg_continut:
    if not user_api_key:
        st.error("⚠️ Introduceți cheia API Gemini în setări pentru a rula analiza!")
    else:
        try:
            client = genai.Client(api_key=user_api_key)
            
            # Construim payload-ul multimodal (Text + Imagine dacă este cazul)
            continut_apel = [msg_continut]
            if imagine_incarcata and metoda_analiza == "Imagine / Captură de ecran":
                continut_apel.append(imagine_incarcata)
                
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=continut_apel,
                config=types.GenerateContentConfig(
                    system_instruction=PROMPT_SISTEM,
                    response_mime_type="application/json"
                )
            )
            
            date_analiza = json.loads(response.text)
            
            # Salvare în istoric sesiune
            st.session_state.istoric_web.insert(0, {
                "data": datetime.now().strftime('%d.%m.%Y %H:%M'),
                "titlu": titlu_articol if metoda_analiza == "Link Articol (URL)" else f"Imagine: {fisier_imagine.name}",
                "verdict": date_analiza['verdict'],
                "scor": date_analiza['scor']
            })
            
            # Afișare casetă rezultat personalizată în funcție de verdict
            clasa_box = "necredibil-box"
            if date_analiza['verdict'] == "CREDIBIL": 
                clasa_box = "credibil-box"
            elif date_analiza['verdict'] == "SUSPICIOS": 
                clasa_box = "suspicios-box"
            
            st.markdown(f"""
                <div class="{clasa_box}">
                    <h2 style='margin:0;'>Verdict: {date_analiza['verdict']} ({date_analiza['scor']}/100)</h2>
                    <p><strong>Ținta analizată:</strong> {titlu_articol if metoda_analiza == "Link Articol (URL)" else fisier_imagine.name}</p>
                    <p style='color: #CCD6E8;'>{date_analiza['sumar']}</p>
                    <p style='color: #8899BB; font-style: italic;'><strong>Recomandare:</strong> {date_analiza['recomandari']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Opțiune descărcare raport rapid text
            raport_text = f"RAPORT VERITAS\nȚinta: {titlu_articol if metoda_analiza == "Link Articol (URL)" else fisier_imagine.name}\nVerdict: {date_analiza['verdict']} ({date_analiza['scor']}/100)\nSumar: {date_analiza['sumar']}"
            st.download_button("📥 Descarcă Raport Text", data=raport_text, file_name="raport_veritas.txt")
            
        except Exception as e:
            st.error(f"❌ Eroare la analiza inteligentă: {str(e)}")

# Afișare Istoric Sesiune
if st.session_state.istoric_web:
    st.write("---")
    st.subheader("📋 Istoricul căutărilor tale din această sesiune")
    for item in st.session_state.istoric_web:
        st.write(f"⏱️ **{item['data']}** | {item['titlu'][:60]}... -> **{item['verdict']}** ({item['scor']}/100)")
