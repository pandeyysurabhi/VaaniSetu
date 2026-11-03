import os
from pathlib import Path
from sarvamai import SarvamAI

# Resolve project root and load .env if present
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

if ENV_PATH.exists():
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

SARVAM_API_KEY = os.environ.get("SARVAM_API_KEY")

def get_sarvam_client() -> SarvamAI:
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("SARVAM_API_KEY")
            if api_key:
                os.environ["SARVAM_API_KEY"] = api_key
        except Exception:
            pass

    if not api_key:
        raise ValueError("SARVAM_API_KEY is not configured in .env, st.secrets, or environment.")
    return SarvamAI(api_subscription_key=api_key)


# Supported Indic Languages for Bulbul & Mayura
SUPPORTED_LANGUAGES = {
    "hi-IN": {"name": "Hindi", "native": "हिन्दी"},
    "en-IN": {"name": "English (India)", "native": "English"},
    "bn-IN": {"name": "Bengali", "native": "বাংলা"},
    "ta-IN": {"name": "Tamil", "native": "தமிழ்"},
    "te-IN": {"name": "Telugu", "native": "తెలుగు"},
    "kn-IN": {"name": "Kannada", "native": "ಕನ್ನಡ"},
    "ml-IN": {"name": "Malayalam", "native": "മലയാളം"},
    "mr-IN": {"name": "Marathi", "native": "मराठी"},
    "gu-IN": {"name": "Gujarati", "native": "ગુજરાતી"},
    "pa-IN": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ"},
    "od-IN": {"name": "Odia", "native": "ଓଡ଼ିଆ"},
}

# Persona presets mapped to speaker IDs and parameters
VOICE_PERSONAS = {
    "storyteller": {
        "title": "Storyteller / Kathakar",
        "description": "Expressive, rich pauses, engaging pacing for fiction, culture, and long-form reading",
        "default_speaker": {
            "hi-IN": "shubh_hi_stories_mixed",
            "en-IN": "aditi_en_stories",
            "default": "roopa"
        },
        "pace": 0.95,
        "pitch": 0.0
    },
    "news": {
        "title": "News Anchor / Bulletin",
        "description": "Authoritative, crisp diction, brisk pacing for circulars, updates, and news",
        "default_speaker": {
            "hi-IN": "anand_hi_news",
            "en-IN": "girish_en_documentary",
            "default": "aditya"
        },
        "pace": 1.08,
        "pitch": 0.0
    },
    "teacher": {
        "title": "Educator / Explainer",
        "description": "Patient, clear articulation, structured cadence for lessons, STEM, and tutorials",
        "default_speaker": {
            "hi-IN": "ritu_hi_edtech",
            "en-IN": "aparna_en_edtech",
            "default": "ritu"
        },
        "pace": 0.98,
        "pitch": 0.0
    },
    "conversational": {
        "title": "Conversational / Casual",
        "description": "Friendly, modern conversational rhythm for podcasts, blogs, and dialogue",
        "default_speaker": {
            "hi-IN": "aditya_hi_conversational",
            "en-IN": "simran_en_conversation",
            "default": "simran"
        },
        "pace": 1.0,
        "pitch": 0.0
    }
}

