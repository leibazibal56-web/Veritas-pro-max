import streamlit as st
import json
import requests
import random
import time
from urllib.parse import urlparse
from datetime import datetime
from bs4 import BeautifulSoup
import anthropic
import base64
from PIL import Image
import io

# ═══════════════════════════════════════════════════════════
# CONFIGURARE PAGINĂ STREAMLIT
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Veritas Pro Max — Fact Checking",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════
# CSS PREMIUM — DARK INTELLIGENCE THEME
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* === ROOT === */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* === APP BACKGROUND === */
.stApp {
    background: #080D1A;
    color: #C8D8F0;
}

/* === SIDEBAR === */
section[data-testid="stSidebar"] {
    background: #0C1220 !important;
    border-right: 1px solid #1E2D4A;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown {
    color: #8BA3C4 !important;
    font-size: 0.85rem;
}

/* === TITLE BADGE === */
.veritas-header {
    text-align: center;
    padding: 2.5rem 0 1rem 0;
}
.veritas-title {
    font-size: 2.1rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #F0F6FF;
    margin: 0;
}
.veritas-subtitle {
    font-size: 0.82rem;
    color: #4A6A8A;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 0.4rem;
    font-family: 'JetBrains Mono', monospace;
}
.veritas-badge {
    display: inline-block;
    background: linear-gradient(135deg, #1A2744, #0D1830);
    border: 1px solid #2A3F6A;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    color: #5B9BFF;
    letter-spacing: 0.08em;
    margin-top: 0.5rem;
}

/* === INPUT FIELDS === */
.stTextInput > div > div > input {
    background: #0C1628 !important;
    border: 1px solid #1E3055 !important;
    border-radius: 8px !important;
    color: #D0E0FF !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    padding: 0.7rem 1rem !important;
    transition: border-color 0.2s ease;
}
.stTextInput > div > div > input:focus {
    border-color: #3A6FBF !important;
    box-shadow: 0 0 0 3px rgba(58, 111, 191, 0.15) !important;
}
.stTextInput > div > div > input::placeholder {
    color: #2E4A6A !important;
}

/* === BUTTON === */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #1A3A7A, #0F2355) !important;
    border: 1px solid #2A4F8A !important;
    color: #A0C4FF !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.65rem 1.5rem !important;
    letter-spacing: 0.03em;
    transition: all 0.2s ease !important;
    cursor: pointer;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1F4490, #122B65) !important;
    border-color: #3A6FBF !important;
    color: #D0E8FF !important;
    box-shadow: 0 0 20px rgba(58, 111, 191, 0.25) !important;
}

/* === RADIO GROUP === */
.stRadio > div {
    gap: 1rem;
}
.stRadio > div > label {
    background: #0C1628 !important;
    border: 1px solid #1A2D4A !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.2rem !important;
    color: #7090B8 !important;
    font-size: 0.88rem !important;
    transition: all 0.2s ease;
}
.stRadio > div > label:has(input:checked) {
    border-color: #3A6FBF !important;
    color: #A0C4FF !important;
    background: #0F1E3A !important;
}

/* === VERDICT CARDS === */
.verdict-card {
    border-radius: 12px;
    padding: 1.8rem 2rem;
    margin: 1.5rem 0;
    position: relative;
    overflow: hidden;
}
.verdict-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.verdict-credibil {
    background: linear-gradient(135deg, #071A10, #0A1F14);
    border: 1px solid #1A4A2A;
}
.verdict-credibil::before { background: linear-gradient(90deg, #00E87A, #00C060); }
.verdict-suspicios {
    background: linear-gradient(135deg, #1A1208, #1F160A);
    border: 1px solid #4A3010;
}
.verdict-suspicios::before { background: linear-gradient(90deg, #FFB347, #FF8C00); }
.verdict-necredibil {
    background: linear-gradient(135deg, #1A0810, #1F0A12);
    border: 1px solid #4A1020;
}
.verdict-necredibil::before { background: linear-gradient(90deg, #FF4070, #E0203A); }

/* === VERDICT HEADER === */
.verdict-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.2rem;
}
.verdict-icon {
    font-size: 1.8rem;
    line-height: 1;
}
.verdict-label {
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: #F0F6FF;
}
.verdict-score {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #4A6A8A;
    letter-spacing: 0.06em;
    margin-top: 0.15rem;
}

/* === DOMAIN TAGS === */
.domain-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin: 0.8rem 0;
}
.domain-tag {
    background: #0C1628;
    border: 1px solid #1A2D4A;
    border-radius: 20px;
    padding: 0.2rem 0.6rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #5080A0;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* === FIELD LABELS === */
.field-label {
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    color: #3A5A7A;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.4rem;
    margin-top: 1rem;
}
.field-value {
    font-size: 0.9rem;
    color: #A0B8D0;
    line-height: 1.6;
}

/* === INDICATOR BARS === */
.indicator-row {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin: 0.4rem 0;
}
.indicator-label {
    font-size: 0.75rem;
    color: #5A7A9A;
    width: 140px;
    flex-shrink: 0;
}
.indicator-bar-bg {
    flex: 1;
    height: 4px;
    background: #0C1628;
    border-radius: 4px;
    overflow: hidden;
}
.indicator-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.6s ease;
}
.indicator-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #3A5A7A;
    width: 30px;
    text-align: right;
}

/* === HISTORY === */
.history-item {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.6rem 0.8rem;
    background: #0A1422;
    border: 1px solid #141F33;
    border-radius: 8px;
    margin: 0.4rem 0;
    font-size: 0.82rem;
}
.history-dot-credibil  { color: #00C060; }
.history-dot-suspicios { color: #FF8C00; }
.history-dot-necredibil{ color: #E0203A; }
.history-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #2A4A6A;
}
.history-title {
    flex: 1;
    color: #6080A0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 200px;
}

/* === DIVIDER === */
.section-divider {
    border: none;
    border-top: 1px solid #121E30;
    margin: 2rem 0;
}

/* === FILE UPLOADER === */
.stFileUploader > div {
    background: #0C1628 !important;
    border: 1px dashed #1E3055 !important;
    border-radius: 8px !important;
}

/* === DOWNLOAD BUTTON === */
.stDownloadButton > button {
    background: transparent !important;
    border: 1px solid #1A2D4A !important;
    color: #4A7AA0 !important;
    border-radius: 6px !important;
    font-size: 0.82rem !important;
    padding: 0.4rem 0.9rem !important;
}
.stDownloadButton > button:hover {
    border-color: #3A6FBF !important;
    color: #80B0E0 !important;
}

/* === SPINNER TEXT === */
.stSpinner > div {
    border-color: #1A3A6A transparent transparent transparent !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div class="veritas-header">
    <div class="veritas-title">🔍 VERITAS PRO MAX</div>
    <div class="veritas-subtitle">Intelligence · Fact-Checking · Dezinformare</div>
    <div class="veritas-badge">v3.0 · Gemini 2.5 Flash · Multi-Domain Analysis</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# SESIUNE & STATE
# ═══════════════════════════════════════════════════════════
if "istoric_web" not in st.session_state:
    st.session_state.istoric_web = []

# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
if "ANTHROPIC_API_KEY" in st.secrets:
    user_api_key = st.secrets["ANTHROPIC_API_KEY"]
else:
    st.sidebar.header("🔑 API Key")
    user_api_key = st.sidebar.text_input("Cheie API Anthropic (Claude):", type="password", value="")

st.sidebar.markdown("""
---
**Veritas Pro Max v3.0**

Motor: `claude-sonnet-4-6`  
Analiză: **multi-domeniu** — politic, juridic, științific, financiar, media  
Extracție: rezistentă la anti-bot, fallback multi-strategie

---
**Domenii de analiză:**
- 🏛️ Politic & Geopolitic
- ⚖️ Juridic & Legislativ  
- 🔬 Științific & Medical
- 💰 Financiar & Economic
- 📱 Media & Social Media
- 🔐 Cybersecurity & Dezinformare
""")

# ═══════════════════════════════════════════════════════════
# FUNCȚII TEHNICE — ROBUST URL EXTRACTOR
# ═══════════════════════════════════════════════════════════
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/124.0",
]

def valideaza_url(url):
    if not url or not url.strip():
        return False, "Introduceți un URL valid."
    parsed = urlparse(url.strip())
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        return False, "URL-ul trebuie să înceapă cu https://..."
    if parsed.hostname in {'localhost', '127.0.0.1', '0.0.0.0'}:
        return False, "Acces nepermis (localhost)."
    return True, url.strip()

def extrage_continut(url, max_retry=3):
    """
    Extractor robust cu:
    - Rotație User-Agent anti-bot
    - Fallback la requests.get simplu dacă primul try eșuează
    - Extracție din <article>, <main>, <div[class*=content]>, <p>
    - Deduplicare paragrafe goale
    - Limite de caractere safe
    - Retry cu backoff exponențial
    """
    last_error = None
    for attempt in range(max_retry):
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ro-RO,ro;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
            session = requests.Session()
            session.max_redirects = 5

            response = session.get(
                url,
                headers=headers,
                timeout=(5, 15),   # (connect, read)
                allow_redirects=True,
                verify=True,
            )

            # Acceptăm și 403/429 parțiale — uneori conțin totuși HTML util
            if response.status_code not in (200, 403, 429):
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Titlu
            titlu = "Titlu necunoscut"
            if soup.title and soup.title.string:
                titlu = soup.title.string.strip()
            elif soup.find('h1'):
                titlu = soup.find('h1').get_text(strip=True)

            # Extracție ierarhizată: <article> > <main> > <div.content> > <p>
            text_brut = ""
            container = (
                soup.find('article') or
                soup.find('main') or
                soup.find('div', class_=lambda c: c and any(
                    kw in c.lower() for kw in ['content', 'article', 'body', 'text', 'post']
                ))
            )

            if container:
                paragrafe = container.find_all(['p', 'h2', 'h3', 'blockquote'], limit=20)
            else:
                paragrafe = soup.find_all('p', limit=20)

            texte_unice = []
            for p in paragrafe:
                t = p.get_text(separator=' ', strip=True)
                if len(t) > 40 and t not in texte_unice:
                    texte_unice.append(t)

            text_brut = " | ".join(texte_unice)

            # Metadata Open Graph dacă textul e slab
            if len(text_brut) < 200:
                og_desc = soup.find('meta', attrs={'property': 'og:description'})
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                extra = ""
                if og_desc and og_desc.get('content'):
                    extra += og_desc['content'] + " "
                if meta_desc and meta_desc.get('content'):
                    extra += meta_desc['content']
                text_brut = extra.strip() + " " + text_brut

            if len(text_brut.strip()) < 100:
                raise Exception(
                    "Conținut insuficient extras — site-ul poate necesita JavaScript sau blochează scraperele."
                )

            return titlu, text_brut[:3000]

        except requests.exceptions.SSLError:
            last_error = "Certificat SSL invalid pe site-ul țintă."
            break
        except requests.exceptions.ConnectionError:
            last_error = "Nu s-a putut stabili conexiunea cu site-ul."
            break
        except requests.exceptions.Timeout:
            last_error = f"Timeout la tentativa {attempt+1}/{max_retry}."
            if attempt < max_retry - 1:
                time.sleep(2 ** attempt)
        except requests.exceptions.TooManyRedirects:
            last_error = "Prea multe redirecționări — URL potențial invalid."
            break
        except Exception as e:
            last_error = str(e)
            if attempt < max_retry - 1:
                time.sleep(1)

    raise Exception(f"Extracție eșuată după {max_retry} tentative: {last_error}")

# ═══════════════════════════════════════════════════════════
# PROMPT MULTI-DOMENIU — RAPORT EXTINS
# ═══════════════════════════════════════════════════════════
PROMPT_SISTEM = """Ești VERITAS, un sistem expert de fact-checking și analiză a dezinformării de nivel intelligence.

INSTRUCȚIUNI OBLIGATORII:
1. Răspunde STRICT în format JSON valid, fără text suplimentar, fără markdown, fără backticks.
2. Analizează textul/imaginea din MULTIPLE domenii simultan: politic, juridic, științific, financiar, media/propagandă, cybersecurity.
3. Identifică tehnicile specifice de manipulare (cherry-picking, false authority, emotional manipulation, gaslighting, whataboutism, astroturfing etc.).

FORMAT JSON OBLIGATORIU:
{
  "scor": <int 0-100, unde 100=complet credibil>,
  "verdict": "<CREDIBIL|SUSPICIOS|NECREDIBIL>",
  "sumar": "<rezumat analitic 3-4 propoziții, obiectiv>",
  "domenii_afectate": ["<domeniu1>", "<domeniu2>"],
  "indicatori": {
    "acuratete_faptica": <int 0-100>,
    "context_corect": <int 0-100>,
    "surse_verificabile": <int 0-100>,
    "limbaj_neutral": <int 0-100>,
    "coerenta_logica": <int 0-100>
  },
  "tehnici_manipulare": ["<tehnică identificată sau null>"],
  "elemente_verificate": ["<fapt/afirmație verificată explicit>"],
  "elemente_problematice": ["<afirmație falsă sau înșelătoare>"],
  "surse_recomandate": ["<sursă de referință pentru verificare>"],
  "recomandari": "<recomandare acțională clară pentru cititor>"
}

CONTEXT FACTUAL ACTUAL (ancorat la realitatea politică din România, 2026):
- Nicușor Dan este Președintele României.
- Pe scena politică există negocieri privind formarea Guvernului.
- Evaluează ținând cont de această realitate.

Returnează EXCLUSIV JSON valid. Niciun alt text."""

# ═══════════════════════════════════════════════════════════
# HELPER — RENDER VERDICT CARD
# ═══════════════════════════════════════════════════════════
def render_verdict(data, target_name):
    verdict = data.get("verdict", "NECUNOSCUT")
    scor = data.get("scor", 0)
    sumar = data.get("sumar", "—")
    recomandari = data.get("recomandari", "—")
    domenii = data.get("domenii_afectate", [])
    indicatori = data.get("indicatori", {})
    tehnici = data.get("tehnici_manipulare", [])
    verificate = data.get("elemente_verificate", [])
    problematice = data.get("elemente_problematice", [])
    surse_rec = data.get("surse_recomandate", [])

    cls_map = {
        "CREDIBIL":   ("verdict-credibil",   "✓", "#00E87A"),
        "SUSPICIOS":  ("verdict-suspicios",  "⚠", "#FFB347"),
        "NECREDIBIL": ("verdict-necredibil", "✕", "#FF4070"),
    }
    card_cls, icon, accent_color = cls_map.get(verdict, ("verdict-necredibil", "?", "#888"))

    # Indicator bars
    def bar(label, value, color):
        return f"""
        <div class="indicator-row">
            <span class="indicator-label">{label}</span>
            <div class="indicator-bar-bg">
                <div class="indicator-bar-fill" style="width:{value}%; background:{color};"></div>
            </div>
            <span class="indicator-value">{value}</span>
        </div>"""

    ind_html = ""
    ind_colors = {
        "acuratete_faptica": "#5B9BFF",
        "context_corect": "#7BC8FF",
        "surse_verificabile": "#A0D8EF",
        "limbaj_neutral": "#80C0F0",
        "coerenta_logica": "#60A8E0",
    }
    ind_labels = {
        "acuratete_faptica": "Acuratețe faptică",
        "context_corect": "Context corect",
        "surse_verificabile": "Surse verificabile",
        "limbaj_neutral": "Limbaj neutru",
        "coerenta_logica": "Coerență logică",
    }
    for k, v in indicatori.items():
        ind_html += bar(ind_labels.get(k, k), v, ind_colors.get(k, "#5B9BFF"))

    # Domain tags
    domain_tags_html = "".join(f'<span class="domain-tag">{d}</span>' for d in domenii)

    # Lists
    def render_list(items, color):
        if not items:
            return "<span style='color:#2A4A6A;font-size:0.82rem;'>Niciun element identificat.</span>"
        return "".join(
            f"<div style='font-size:0.85rem;color:{color};margin:0.3rem 0;padding-left:0.8rem;border-left:2px solid {color}30;'>{item}</div>"
            for item in items if item
        )

    tehnici_html = "".join(
        f"<span style='background:#1A0D20;border:1px solid #3A1A4A;border-radius:12px;padding:0.15rem 0.5rem;font-size:0.72rem;color:#A070C0;font-family:JetBrains Mono,monospace;margin:0.2rem;display:inline-block;'>{t}</span>"
        for t in tehnici if t
    ) or "<span style='color:#2A4A6A;font-size:0.82rem;'>Nicio tehnică detectată.</span>"

    st.markdown(f"""
    <div class="verdict-card {card_cls}">
        <div class="verdict-header">
            <span class="verdict-icon" style="color:{accent_color};">{icon}</span>
            <div>
                <div class="verdict-label">{verdict}</div>
                <div class="verdict-score">SCOR CREDIBILITATE: {scor}/100 · {target_name[:50]}</div>
            </div>
        </div>

        <div class="domain-tags">{domain_tags_html}</div>

        <div class="field-label">Sumar Analitic</div>
        <div class="field-value">{sumar}</div>

        <div class="field-label">Indicatori de Calitate</div>
        {ind_html}

        <div class="field-label">Tehnici de Manipulare Detectate</div>
        <div style="margin:0.5rem 0;">{tehnici_html}</div>

        <div class="field-label">Elemente Verificate ✓</div>
        {render_list(verificate, '#00A050')}

        <div class="field-label">Elemente Problematice ✗</div>
        {render_list(problematice, '#C03050')}

        <div class="field-label">Surse Recomandate pentru Verificare</div>
        {render_list(surse_rec, '#4A7AA0')}

        <div class="field-label">Recomandare</div>
        <div class="field-value" style="font-style:italic;color:#7090B0;">{recomandari}</div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# SELECȚIE MOD ANALIZĂ
# ═══════════════════════════════════════════════════════════
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
metoda_analiza = st.radio(
    "Alege tipul de analiză:",
    ("🔗 Link Articol (URL)", "🖼️ Imagine / Captură de ecran"),
    horizontal=True
)

titlu_articol = "Analiză vizuală"
msg_continut = ""
imagine_incarcata = None
fisier_imagine = None
data_azi = datetime.now().strftime('%d.%m.%Y')

# ═══════════════════════════════════════════════════════════
# MOD URL
# ═══════════════════════════════════════════════════════════
if "URL" in metoda_analiza:
    url_tinta = st.text_input(
        "URL articol:",
        placeholder="https://stiripesurse.ro/articol-de-verificat",
        label_visibility="collapsed"
    )
    if st.button("🔍 Analizează Articolul"):
        este_valid, rezultat_url = valideaza_url(url_tinta)
        if not este_valid:
            st.error(rezultat_url)
        else:
            with st.spinner("Extragem conținut și rulăm analiza multi-domeniu..."):
                try:
                    titlu_articol, text_articol = extrage_continut(rezultat_url)
                    msg_continut = (
                        f"Data curentă reală: {data_azi}.\n"
                        f"Sursă: {rezultat_url}\n"
                        f"Titlu: {titlu_articol}\n"
                        f"Conținut extras: {text_articol}"
                    )
                except Exception as e:
                    st.error(f"⚠️ {str(e)}")

# ═══════════════════════════════════════════════════════════
# MOD IMAGINE
# ═══════════════════════════════════════════════════════════
else:
    fisier_imagine = st.file_uploader(
        "Încarcă captură de ecran (PNG, JPG, JPEG):",
        type=["png", "jpg", "jpeg"]
    )
    if fisier_imagine is not None:
        imagine_incarcata = Image.open(fisier_imagine)
        st.image(imagine_incarcata, caption="Imagine încărcată", use_container_width=True)
        titlu_articol = fisier_imagine.name

        if st.button("🔍 Analizează Imaginea"):
            msg_continut = (
                f"Data curentă reală: {data_azi}.\n"
                "Analizează conținutul vizual și textul din această imagine. "
                "Extrage mesajul principal, verifică faptele, identifică tehnici de dezinformare vizuală "
                "(manipulare foto, context fals, citate falsificate etc.)."
            )

# ═══════════════════════════════════════════════════════════
# EXECUȚIE GEMINI API + AFIȘARE
# ═══════════════════════════════════════════════════════════
if msg_continut:
    if not user_api_key:
        st.error("⚠️ Adaugă cheia API Anthropic în sidebar pentru a rula analiza.")
    else:
        try:
            client = anthropic.Anthropic(api_key=user_api_key)

            # Construim conținutul mesajului — text + imagine dacă există
            continut_mesaj = []
            if imagine_incarcata and "Imagine" in metoda_analiza:
                # Convertim PIL Image în base64 pentru API-ul Anthropic
                buf = io.BytesIO()
                fmt = imagine_incarcata.format or "PNG"
                imagine_incarcata.save(buf, format=fmt)
                img_b64 = base64.standard_b64encode(buf.getvalue()).decode("utf-8")
                media_type_map = {"PNG": "image/png", "JPEG": "image/jpeg", "JPG": "image/jpeg", "WEBP": "image/webp"}
                media_type = media_type_map.get(fmt.upper(), "image/png")
                continut_mesaj.append({
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": img_b64}
                })
            continut_mesaj.append({"type": "text", "text": msg_continut})

            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                system=PROMPT_SISTEM,
                messages=[{"role": "user", "content": continut_mesaj}]
            )

            # Parse robust — curăță eventuale backticks reziduale
            raw_text = response.content[0].text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.rstrip("`").strip()
            date_analiza = json.loads(raw_text)

            # Salvare istoric
            st.session_state.istoric_web.insert(0, {
                "data": datetime.now().strftime('%d.%m.%Y %H:%M'),
                "titlu": titlu_articol,
                "verdict": date_analiza.get("verdict", "?"),
                "scor": date_analiza.get("scor", 0)
            })

            # Render card
            render_verdict(date_analiza, titlu_articol)

            # Descărcare raport JSON complet
            raport_json = json.dumps(date_analiza, ensure_ascii=False, indent=2)
            raport_text = (
                f"RAPORT VERITAS PRO MAX v3.0\n"
                f"Data: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
                f"Ținta: {titlu_articol}\n"
                f"Verdict: {date_analiza.get('verdict')} ({date_analiza.get('scor')}/100)\n\n"
                f"Sumar:\n{date_analiza.get('sumar', '')}\n\n"
                f"Recomandare:\n{date_analiza.get('recomandari', '')}\n\n"
                f"JSON complet:\n{raport_json}"
            )

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📥 Descarcă Raport TXT",
                    data=raport_text,
                    file_name=f"veritas_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )
            with col2:
                st.download_button(
                    "📊 Descarcă JSON Complet",
                    data=raport_json,
                    file_name=f"veritas_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json"
                )

        except json.JSONDecodeError as e:
            st.error(f"❌ Răspunsul AI nu a putut fi parsat ca JSON: {str(e)}")
            with st.expander("Răspuns brut (debug)"):
                st.code(response.content[0].text if 'response' in dir() else "Niciun răspuns", language="text")
        except Exception as e:
            st.error(f"❌ Eroare la analiza Gemini: {str(e)}")

# ═══════════════════════════════════════════════════════════
# ISTORIC SESIUNE
# ═══════════════════════════════════════════════════════════
if st.session_state.istoric_web:
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.72rem;font-family:JetBrains Mono,monospace;color:#2A4A6A;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.8rem;'>Istoric sesiune</div>",
        unsafe_allow_html=True
    )
    for item in st.session_state.istoric_web[:10]:
        dot_cls = f"history-dot-{item['verdict'].lower()}"
        dot_sym = {"CREDIBIL": "●", "SUSPICIOS": "◆", "NECREDIBIL": "■"}.get(item["verdict"], "?")
        st.markdown(f"""
        <div class="history-item">
            <span class="{dot_cls}">{dot_sym}</span>
            <span class="history-meta">{item['data']}</span>
            <span class="history-title">{item['titlu'][:55]}</span>
            <span style="font-family:JetBrains Mono,monospace;font-size:0.72rem;color:#3A5A7A;white-space:nowrap;">
                {item['verdict']} · {item['scor']}/100
            </span>
        </div>
        """, unsafe_allow_html=True)
