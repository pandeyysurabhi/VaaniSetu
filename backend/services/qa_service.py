import io
from typing import Dict, Any, Optional
from backend.config import get_sarvam_client, SUPPORTED_LANGUAGES
from backend.services.tts_service import synthesize_speech

def transcribe_audio_query(
    audio_bytes: bytes,
    filename: str = "query.wav",
    content_type: str = "audio/wav",
    language_code: str = "unknown"
) -> str:
    """
    Uses Sarvam Saaras to transcribe a spoken voice query from the user.
    """
    client = get_sarvam_client()
    file_tuple = (filename, io.BytesIO(audio_bytes), content_type)
    
    resp = client.speech_to_text.transcribe(
        file=file_tuple,
        model="saaras:v3",
        language_code=language_code
    )
    return (resp.transcript or "").strip()

def answer_document_question(
    context_text: str,
    question: str,
    language_code: str = "hi-IN"
) -> Dict[str, Any]:
    """
    Answers a user's question about the current text/document using sarvam-105b-conversations,
    and synthesizes a natural voice audio reply using Bulbul.
    """
    if not question.strip():
        raise ValueError("Question cannot be empty.")
    if not context_text.strip():
        raise ValueError("Document context cannot be empty.")

    client = get_sarvam_client()
    lang_name = SUPPORTED_LANGUAGES.get(language_code, {}).get("name", "Hindi")

    system_prompt = (
        "You are an interactive AI audio reading companion. "
        "The user is listening to an article/document and has asked a clarifying question. "
        "Answer their question clearly, warmly, and concisely (2 to 3 sentences) based on the provided document context. "
        f"Answer directly in {lang_name} using natural spoken phrasing suitable for voice output. "
        "Do not include markdown symbols, bullet lists, or greetings like 'Sure!'. Just give the direct answer."
    )

    user_prompt = f"Document Context:\n{context_text[:3000]}\n\nUser Question:\n{question}"

    response = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.4,
        max_tokens=350
    )

    answer_text = response.choices[0].message.content.strip()

    # Synthesize the answer into voice audio
    audio_res = synthesize_speech(
        text=answer_text,
        language_code=language_code,
        persona="teacher",
        pace=1.05
    )

    return {
        "question": question,
        "answer_text": answer_text,
        "language_code": language_code,
        "audio_data_uri": audio_res["audio_data_uri"],
        "audio_base64": audio_res["audio_base64"]
    }

