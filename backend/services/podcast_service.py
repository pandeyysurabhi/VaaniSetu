import base64
from typing import List, Dict, Any, Optional
from backend.config import get_sarvam_client

# Preset complementary voice pairs for dual-speaker podcasting
PODCAST_VOICE_PAIRS = {
    "hi-IN": {
        "host1": {"name": "Aarav", "speaker": "aditya", "model": "bulbul:v3", "pace": 1.05},
        "host2": {"name": "Meera", "speaker": "roopa", "model": "bulbul:v3", "pace": 0.98}
    },
    "en-IN": {
        "host1": {"name": "Aarav", "speaker": "aditya", "model": "bulbul:v3", "pace": 1.05},
        "host2": {"name": "Meera", "speaker": "simran", "model": "bulbul:v3", "pace": 1.0}
    },
    "ta-IN": {
        "host1": {"name": "Aarav", "speaker": "vijay", "model": "bulbul:v3", "pace": 1.0},
        "host2": {"name": "Meera", "speaker": "gokul", "model": "bulbul:v3", "pace": 1.0}
    },
    "default": {
        "host1": {"name": "Aarav", "speaker": "aditya", "model": "bulbul:v3", "pace": 1.0},
        "host2": {"name": "Meera", "speaker": "roopa", "model": "bulbul:v3", "pace": 1.0}
    }
}

def synthesize_podcast(
    turns: List[Dict[str, str]],
    language_code: str = "hi-IN"
) -> Dict[str, Any]:
    """
    Synthesizes a multi-turn, dual-speaker podcast conversation into a single
    seamless audio track, with distinct voices for Host 1 and Host 2.
    """
    if not turns:
        raise ValueError("Podcast dialogue turns cannot be empty.")

    client = get_sarvam_client()
    pair = PODCAST_VOICE_PAIRS.get(language_code, PODCAST_VOICE_PAIRS["default"])

    all_audio_bytes = []
    enhanced_turns = []

    for turn_idx, turn in enumerate(turns):
        speaker_key = turn.get("speaker", "host1").lower()
        if speaker_key not in ["host1", "host2"]:
            speaker_key = "host1" if turn_idx % 2 == 0 else "host2"

        host_meta = pair[speaker_key]
        line_text = turn.get("text", "").strip()

        if not line_text:
            continue

        resp = client.text_to_speech.convert(
            text=line_text,
            language_code=language_code,
            speaker=host_meta["speaker"],
            model=host_meta["model"],
            pace=host_meta["pace"],
            output_audio_codec="mp3",
            enable_preprocessing=True
        )

        for b64 in resp.audios:
            all_audio_bytes.append(base64.b64decode(b64))

        enhanced_turns.append({
            "speaker_id": speaker_key,
            "speaker_name": host_meta["name"],
            "speaker_voice": host_meta["speaker"],
            "text": line_text
        })

    combined_bytes = b"".join(all_audio_bytes)
    combined_b64 = base64.b64encode(combined_bytes).decode("utf-8")
    data_uri = f"data:audio/mpeg;base64,{combined_b64}"

    return {
        "audio_base64": combined_b64,
        "audio_data_uri": data_uri,
        "audio_format": "mp3",
        "language_code": language_code,
        "turns": enhanced_turns,
        "turn_count": len(enhanced_turns)
    }

