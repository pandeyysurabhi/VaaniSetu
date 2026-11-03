import base64
import re
from typing import Optional, List, Dict, Any
from backend.config import get_sarvam_client, VOICE_PERSONAS, SUPPORTED_LANGUAGES
from backend.services.translation_service import split_text_into_chunks

def resolve_speaker_and_params(
    language_code: str,
    persona: Optional[str] = None,
    speaker: Optional[str] = None,
    pace: Optional[float] = None,
    pitch: Optional[float] = None,
    model: str = "bulbul:v3"
) -> Dict[str, Any]:
    """
    Resolves optimal speaker, model, and prosody parameters based on persona and language.
    """
    resolved_pace = pace if pace is not None else 1.0
    resolved_pitch = pitch if pitch is not None else 0.0
    resolved_model = model

    if persona and persona in VOICE_PERSONAS:
        p_info = VOICE_PERSONAS[persona]
        if pace is None:
            resolved_pace = p_info["pace"]
        if pitch is None:
            resolved_pitch = p_info["pitch"]
        
        # If no explicit speaker was provided, pick from persona
        if not speaker:
            spk_map = p_info["default_speaker"]
            speaker = spk_map.get(language_code, spk_map.get("default", "roopa"))
            # If persona uses specialized speaker like 'anand_hi_news' or 'shubh_hi_stories_mixed', switch to bulbul:v4-flash
            if "_" in speaker:
                resolved_model = "bulbul:v4-flash"

    # Default fallback speaker if still empty
    if not speaker:
        speaker = "roopa" if language_code == "hi-IN" else "aditya"

    return {
        "speaker": speaker,
        "pace": resolved_pace,
        "pitch": resolved_pitch,
        "model": resolved_model
    }

def synthesize_speech(
    text: str,
    language_code: str = "hi-IN",
    persona: Optional[str] = None,
    speaker: Optional[str] = None,
    pace: Optional[float] = None,
    pitch: Optional[float] = None,
    model: str = "bulbul:v3",
    output_audio_codec: str = "mp3"
) -> Dict[str, Any]:
    """
    Synthesizes speech from text using Sarvam Bulbul. Handles long texts by chunking
    and returns combined base64 audio and metadata.
    """
    if not text.strip():
        raise ValueError("Text cannot be empty for speech synthesis.")

    client = get_sarvam_client()
    params = resolve_speaker_and_params(
        language_code=language_code,
        persona=persona,
        speaker=speaker,
        pace=pace,
        pitch=pitch,
        model=model
    )

    # Bulbul allows up to 2500 chars; we chunk conservatively at 1800 chars
    chunks = split_text_into_chunks(text, max_chars=1800)
    audio_bytes_list = []

    for chunk in chunks:
        resp = client.text_to_speech.convert(
            text=chunk,
            language_code=language_code,
            speaker=params["speaker"],
            pace=params["pace"],
            pitch=params["pitch"],
            model=params["model"],
            output_audio_codec=output_audio_codec,
            enable_preprocessing=True
        )
        for b64_audio in resp.audios:
            audio_bytes = base64.b64decode(b64_audio)
            audio_bytes_list.append(audio_bytes)

    # Combine audio chunks (raw MP3 chunks concatenate cleanly)
    combined_bytes = b"".join(audio_bytes_list)
    combined_b64 = base64.b64encode(combined_bytes).decode("utf-8")
    mime_type = "audio/mpeg" if output_audio_codec == "mp3" else f"audio/{output_audio_codec}"
    data_uri = f"data:{mime_type};base64,{combined_b64}"

    # Generate sentence breakdown for synchronized playback
    sentences = [s.strip() for s in re.split(r'(?<=[.!?।])\s+', text) if s.strip()]

    return {
        "audio_base64": combined_b64,
        "audio_data_uri": data_uri,
        "audio_format": output_audio_codec,
        "language_code": language_code,
        "speaker": params["speaker"],
        "model": params["model"],
        "pace": params["pace"],
        "pitch": params["pitch"],
        "chunk_count": len(chunks),
        "sentences": sentences
    }
