import streamlit as st
import json
import requests
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# CONFIGURARE ȘI UI
# ═══════════════════════════════════════════════════════════
st.set_page_config(page_title="Veritas Pro Max", page_icon="🔍", layout="centered")

st.title("🔍 VERITAS PRO MAX v4.6")
API_KEY = st.secrets.get("GEMINI_API_KEY")

# ═══════════════════════════════════════════════════════════
# LOGICA API (CORECȚIE: REST API Standard)
# ═══════════════════════════════════════════════════════════
def apeleaza_gemini(continut_text):
