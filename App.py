import streamlit as st
import json
import requests
from urllib.parse import urlparse
from datetime import datetime
from bs4 import BeautifulSoup
from PIL import Image
import io

# ═══════════════════════════════════════════════════════════
# CONFIGURARE PAGINĂ ȘI STILURI
# ═══════════════════════════════════════════════════════════
st.set_page_config(page_title="Veritas Pro Max", page_icon="🔍", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0F1628; color: #F0F4FF; }
    .credibil-box { border-left: 5px solid #4FFFB0; padding: 15px; background: #162033; border-radius: 8px; }
    .suspicios-box { border-left: 5px solid #FF6B35; padding: 15px; background: #162033; border-radius: 8px; }
    .necredibil-box { border-left: 5px solid #FF3366; padding: 15px; background: #162033; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 VERITAS PRO MAX v4.2")
API_KEY = st.secrets.get("GEMINI_API_KEY")

# ═══════════════════════════════════════════════════════════
# FUNCȚII TEHNICE
# ═══════════════════════════════════════════════════════════
def apeleaza_gemini(continut_text, imagine=None):
    # Folosim versiunea stabilă 1.5-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    # Construim structura corectă pentru API
    payload = {
        "contents": [{"parts": [{"text": continut_text}]}],
        "generationConfig": {"response_mime_type": "application/json"}
