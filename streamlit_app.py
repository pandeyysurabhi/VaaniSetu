import os
import streamlit as st
from backend.config import SUPPORTED_LANGUAGES, VOICE_PERSONAS, SARVAM_API_KEY
from backend.services.tts_service import synthesize_speech
from backend.services.translation_service import translate_text, detect_language
from backend.services.script_service import simplify_text, summarize_text, generate_podcast_script
from backend.services.podcast_service import synthesize_podcast
from backend.services.document_service import extract_text_from_file
from backend.services.qa_service import answer_document_question

# Page configuration
st.set_page_config(
    page_title="VaaniSetu (वाणीसेतु) — Indic Audio Studio",
    page_icon="🎙️",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #f59e0b; margin-bottom: 0px; }
    .sub-title { font-size: 1rem; color: #9ca3af; margin-bottom: 20px; }
    .host1-card { background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 10px; border-radius: 8px; margin-bottom: 8px; }
    .host2-card { background: rgba(236, 72, 153, 0.1); border-left: 4px solid #ec4899; padding: 10px; border-radius: 8px; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎙️ VaaniSetu (वाणीसेतु)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Indic Audio Intelligence & Voice Companion • Powered by Sarvam AI</div>', unsafe_allow_html=True)

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Studio Settings")
    
    # Check API Key
    api_key_env = os.environ.get("SARVAM_API_KEY")
    api_key_secret = st.secrets.get("SARVAM_API_KEY", None) if hasattr(st, "secrets") else None
    active_key = api_key_env or api_key_secret
    
    if not active_key:
        user_key = st.text_input("Enter Sarvam API Key", type="password")
        if user_key:
            os.environ["SARVAM_API_KEY"] = user_key
            st.success("API Key set!")
    else:
        st.success("✅ Sarvam AI Connected")

    # Language selection
    lang_options = list(SUPPORTED_LANGUAGES.keys())
    selected_lang = st.selectbox(
        "Spoken Language",
        options=lang_options,
        index=0,
        format_func=lambda code: f"{SUPPORTED_LANGUAGES[code]['name']} ({SUPPORTED_LANGUAGES[code]['native']})"
    )

    # Voice Persona
    persona_options = list(VOICE_PERSONAS.keys())
    selected_persona = st.selectbox(
        "Voice Persona",
        options=persona_options,
        index=0,
        format_func=lambda p: VOICE_PERSONAS[p]["title"]
    )

    # Pace slider
    pace = st.slider("Pacing / Speed", min_value=0.8, max_value=1.4, value=1.0, step=0.05)

    st.markdown("---")
    st.subheader("📎 Ingestion Presets")
    samples = {
        "🌾 PM Kisan Circular": "The Central Government has initiated the PM Kisan Samman Nidhi Scheme to provide financial assistance to small and marginal farmers across all states. Under this initiative, eligible landholding farmer families receive direct income support of six thousand rupees per year, deposited directly into their Aadhaar-linked bank accounts in three equal installments.",
        "🚀 ISRO Space News": "India's space exploration agency, ISRO, has successfully placed multiple high-resolution communication satellites into low earth orbit. The payload was launched aboard the heavy-lift launch vehicle, marking another milestone for indigenous aerospace technology.",
        "📖 Panchatantra Fable": "A thirsty crow flew over the villages in search of water. After hours of wandering under the blazing sun, he spotted a small clay pitcher in an orchard. But the water was at the very bottom, beyond the reach of his beak. Thinking patiently, the clever bird picked up small pebbles one by one and dropped them into the pot until the water rose to the brim."
    }
    
    selected_preset = st.selectbox("Load Sample", ["-- Choose a preset --"] + list(samples.keys()))

# Ingestion Section
col_left, col_right = st.columns([1.1, 0.9])

with col_left:
    st.subheader("📝 Input Content")
    
    # Upload document
    uploaded_file = st.file_uploader("Upload PDF or Text Document", type=["pdf", "txt", "md"])
    default_text = ""
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        extracted = extract_text_from_file(uploaded_file.name, file_bytes)
        default_text = extracted["text"]
        st.info(f"Loaded {extracted['char_count']} characters from {uploaded_file.name}")
    elif selected_preset != "-- Choose a preset --":
        default_text = samples[selected_preset]

    input_text = st.text_area("Source Text", value=default_text, height=220, placeholder="Paste text or upload a PDF above...")

# Mode selection & Generation Tabs
with col_right:
    st.subheader("🎧 Studio Output")
    tab_narrate, tab_simplify, tab_brief, tab_podcast = st.tabs([
        "📖 Narration",
        "💡 Samjhaav",
        "⚡ 60s Brief",
        "🎙️ Podcast"
    ])

    with tab_narrate:
        if st.button("Generate Audio Narration", key="btn_narrate", use_container_width=True):
            if not input_text.strip():
                st.warning("Please provide input text.")
            else:
                with st.spinner("Synthesizing audio with Sarvam Bulbul..."):
                    # Detect & translate if needed
                    det = detect_language(input_text)
                    source_lang = det.get("language_code", "en-IN")
                    text_to_speak = input_text
                    if source_lang != selected_lang:
                        trans = translate_text(input_text, target_language_code=selected_lang, source_language_code=source_lang)
                        text_to_speak = trans["translated_text"]

                    res = synthesize_speech(
                        text=text_to_speak,
                        language_code=selected_lang,
                        persona=selected_persona,
                        pace=pace
                    )
                    import base64
                    audio_bytes = base64.b64decode(res["audio_base64"])
                    st.audio(audio_bytes, format="audio/mp3")
                    st.download_button("⬇️ Download MP3", data=audio_bytes, file_name="vaanisetu_narration.mp3", mime="audio/mp3")
                    st.markdown("**Transcript:**")
                    st.write(text_to_speak)

    with tab_simplify:
        if st.button("Simplify & Narrate (Samjhaav)", key="btn_simplify", use_container_width=True):
            if not input_text.strip():
                st.warning("Please provide input text.")
            else:
                with st.spinner("Simplifying jargon with sarvam-105b..."):
                    lang_name = SUPPORTED_LANGUAGES[selected_lang]["name"]
                    simplified = simplify_text(input_text, language_name=lang_name)
                    res = synthesize_speech(
                        text=simplified,
                        language_code=selected_lang,
                        persona=selected_persona,
                        pace=pace
                    )
                    import base64
                    audio_bytes = base64.b64decode(res["audio_base64"])
                    st.audio(audio_bytes, format="audio/mp3")
                    st.download_button("⬇️ Download MP3", data=audio_bytes, file_name="samjhaav_narration.mp3", mime="audio/mp3")
                    st.markdown("**Plain Language Explanation:**")
                    st.write(simplified)

    with tab_brief:
        if st.button("Generate 60-Second Audio Brief", key="btn_brief", use_container_width=True):
            if not input_text.strip():
                st.warning("Please provide input text.")
            else:
                with st.spinner("Generating 60-second summary..."):
                    lang_name = SUPPORTED_LANGUAGES[selected_lang]["name"]
                    summary = summarize_text(input_text, language_name=lang_name)
                    res = synthesize_speech(
                        text=summary,
                        language_code=selected_lang,
                        persona="news",
                        pace=1.08
                    )
                    import base64
                    audio_bytes = base64.b64decode(res["audio_base64"])
                    st.audio(audio_bytes, format="audio/mp3")
                    st.download_button("⬇️ Download MP3", data=audio_bytes, file_name="audio_brief.mp3", mime="audio/mp3")
                    st.markdown("**Summary:**")
                    st.write(summary)

    with tab_podcast:
        if st.button("Generate Dual-Speaker Podcast (Aarav & Meera)", key="btn_podcast", use_container_width=True):
            if not input_text.strip():
                st.warning("Please provide input text.")
            else:
                with st.spinner("sarvam-105b is scripting & synthesizing dual-speaker podcast..."):
                    lang_name = SUPPORTED_LANGUAGES[selected_lang]["name"]
                    turns = generate_podcast_script(input_text, language_name=lang_name)
                    res = synthesize_podcast(turns, language_code=selected_lang)
                    import base64
                    audio_bytes = base64.b64decode(res["audio_base64"])
                    st.audio(audio_bytes, format="audio/mp3")
                    st.download_button("⬇️ Download Podcast MP3", data=audio_bytes, file_name="vaanisetu_podcast.mp3", mime="audio/mp3")
                    st.markdown("**Podcast Dialogue:**")
                    for t in res["turns"]:
                        card_class = "host1-card" if t["speaker_id"] == "host1" else "host2-card"
                        host_label = "🎙️ Aarav (Host)" if t["speaker_id"] == "host1" else "🎓 Meera (Expert)"
                        st.markdown(f'<div class="{card_class}"><b>{host_label}</b>: {t["text"]}</div>', unsafe_allow_html=True)

    # Q&A Companion
    st.markdown("---")
    st.subheader("💬 Voice & Text Companion")
    user_q = st.text_input("Ask a question about the document:")
    if st.button("Ask Companion"):
        if not user_q or not input_text:
            st.warning("Please provide both document text and a question.")
        else:
            with st.spinner("Answering with sarvam-105b..."):
                qa_res = answer_document_question(input_text, user_q, language_code=selected_lang)
                import base64
                qa_audio = base64.b64decode(qa_res["audio_base64"])
                st.write(f"**Answer:** {qa_res['answer_text']}")
                st.audio(qa_audio, format="audio/mp3")
