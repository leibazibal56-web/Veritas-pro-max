import streamlit as st
import json
import requests
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# CONFIGURARE ȘI UI
# ═══════════════════════════════════════════════════════════
st.set_page_config(page_title="Veritas Pro Max", page_icon="🔍", layout="centered")

st.title("🔍 VERITAS PRO MAX v4.4")
API_KEY = st.secrets.get("GEMINI_API_KEY")

# ═══════════════════════════════════════════════════════════
# LOGICA API (CORECȚIE: v1 + flash-002)
# ═══════════════════════════════════════════════════════════
def apeleaza_gemini(continut_text):
    # Corecție endpoint: v1 (stabil) și modelul 002
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-002:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": continut_text}]}],
        "generationConfig": {"response_mime_type": "application
