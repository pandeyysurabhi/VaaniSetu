import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from backend.config import SUPPORTED_LANGUAGES, VOICE_PERSONAS, SARVAM_API_KEY
from backend.services.tts_service import synthesize_speech
from backend.services.translation_service import translate_text, detect_language
from backend.services.script_service import simplify_text, summarize_text, generate_podcast_script
from backend.services.podcast_service import synthesize_podcast
from backend.services.document_service import extract_text_from_file
from backend.services.qa_service import answer_document_question, transcribe_audio_query

app = FastAPI(
    title="VaaniSetu (वाणीसेतु) API",
    description="Indic Audio Intelligence & Accessibility Platform powered by Sarvam AI",
    version="3.0.0"
)

# CORS middleware for local development and web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class TranslationRequest(BaseModel):
    text: str = Field(..., description="Source text to translate")
    target_language_code: str = Field(..., description="Target Indic language code (e.g., hi-IN, ta-IN)")
    source_language_code: str = Field(default="auto", description="Source language code or 'auto'")
    mode: str = Field(default="formal", description="Mode: formal, modern-colloquial, classic-colloquial, code-mixed")

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize")
    language_code: str = Field(default="hi-IN", description="Language code (e.g. hi-IN, en-IN, ta-IN)")
    persona: Optional[str] = Field(default=None, description="Persona preset: storyteller, news, teacher, conversational")
    speaker: Optional[str] = Field(default=None, description="Specific Bulbul speaker ID")
    pace: Optional[float] = Field(default=None, description="Pacing multiplier (0.5 to 2.0)")
    pitch: Optional[float] = Field(default=None, description="Pitch modifier (-1.0 to 1.0)")
    model: str = Field(default="bulbul:v3", description="Bulbul model version: bulbul:v3 or bulbul:v4-flash")
    output_audio_codec: str = Field(default="mp3", description="Audio codec: mp3, wav")

class NarrationRequest(BaseModel):
    text: str = Field(..., description="Input text to narrate")
    target_language_code: str = Field(default="hi-IN", description="Language for final audio")
    source_language_code: str = Field(default="auto", description="Source text language or auto")
    persona: Optional[str] = Field(default="storyteller", description="Voice persona")
    speaker: Optional[str] = Field(default=None, description="Specific speaker if overriding persona")
    pace: Optional[float] = Field(default=None, description="Pace override")
    pitch: Optional[float] = Field(default=None, description="Pitch override")

class AdaptRequest(BaseModel):
    text: str = Field(..., description="Source text to adapt")
    mode: str = Field(default="simplify", description="Adaptation mode: simplify, summary, podcast")
    target_language_code: str = Field(default="hi-IN", description="Target Indic language")

class PodcastRequest(BaseModel):
    text: Optional[str] = Field(default=None, description="Input text to convert to podcast")
    turns: Optional[List[Dict[str, str]]] = Field(default=None, description="Pre-generated dialogue turns")
    target_language_code: str = Field(default="hi-IN", description="Spoken language code for podcast")

class QARequest(BaseModel):
    context_text: str = Field(..., description="The document or article text being discussed")
    question: str = Field(..., description="The user's question about the text")
    language_code: str = Field(default="hi-IN", description="Language code for the response")

# Endpoints (Dual decorators support both direct calls and Vercel stripped prefixes)
@app.get("/api/health")
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "VaaniSetu Audio Intelligence",
        "sarvam_configured": bool(SARVAM_API_KEY),
        "version": "3.0.0"
    }

@app.get("/api/languages")
@app.get("/languages")
def get_languages():
    return {"languages": SUPPORTED_LANGUAGES}

@app.get("/api/personas")
@app.get("/personas")
def get_personas():
    return {"personas": VOICE_PERSONAS}

@app.post("/api/detect-language")
@app.post("/detect-language")
def api_detect_language(payload: dict):
    text = payload.get("text", "")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text field cannot be empty.")
    try:
        result = detect_language(text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/translate")
@app.post("/translate")
def api_translate(req: TranslationRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    try:
        result = translate_text(
            text=req.text,
            target_language_code=req.target_language_code,
            source_language_code=req.source_language_code,
            mode=req.mode
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts")
@app.post("/tts")
def api_tts(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    try:
        result = synthesize_speech(
            text=req.text,
            language_code=req.language_code,
            persona=req.persona,
            speaker=req.speaker,
            pace=req.pace,
            pitch=req.pitch,
            model=req.model,
            output_audio_codec=req.output_audio_codec
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/narrate")
@app.post("/narrate")
def api_narrate(req: NarrationRequest):
    """
    Combined narration pipeline:
    1. Detects language if auto
    2. Translates if target language differs from source
    3. Synthesizes expressive audio using chosen persona
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    try:
        translated_text = req.text
        source_lang = req.source_language_code

        if req.source_language_code == "auto":
            det = detect_language(req.text)
            source_lang = det.get("language_code", "en-IN")

        if source_lang != req.target_language_code:
            trans_res = translate_text(
                text=req.text,
                source_language_code=source_lang,
                target_language_code=req.target_language_code
            )
            translated_text = trans_res["translated_text"]

        tts_res = synthesize_speech(
            text=translated_text,
            language_code=req.target_language_code,
            persona=req.persona,
            speaker=req.speaker,
            pace=req.pace,
            pitch=req.pitch
        )

        return {
            "original_text": req.text,
            "source_language_code": source_lang,
            "translated_text": translated_text,
            "target_language_code": req.target_language_code,
            "persona": req.persona,
            **tts_res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/adapt")
@app.post("/adapt")
def api_adapt(req: AdaptRequest):
    """
    Uses sarvam-105b to transform source text:
    - simplify: plain language explainer (Samjhaav)
    - summary: 60-second audio brief
    - podcast: dual-speaker conversational dialogue script
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    lang_name = SUPPORTED_LANGUAGES.get(req.target_language_code, {}).get("name", "Hindi")
    try:
        if req.mode == "simplify":
            adapted = simplify_text(req.text, language_name=lang_name)
            return {"mode": req.mode, "adapted_text": adapted, "language": lang_name}
        elif req.mode == "summary":
            adapted = summarize_text(req.text, language_name=lang_name)
            return {"mode": req.mode, "adapted_text": adapted, "language": lang_name}
        elif req.mode == "podcast":
            turns = generate_podcast_script(req.text, language_name=lang_name)
            return {"mode": req.mode, "turns": turns, "language": lang_name}
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported mode: {req.mode}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/podcast")
@app.post("/podcast")
def api_podcast(req: PodcastRequest):
    """
    NotebookLM for Bharat: Converts input text into a complete, multi-speaker
    conversational podcast with 2 distinct voices (Host 1 & Host 2).
    """
    try:
        lang_name = SUPPORTED_LANGUAGES.get(req.target_language_code, {}).get("name", "Hindi")
        turns = req.turns
        
        # If turns not provided, generate script using sarvam-105b
        if not turns:
            if not req.text or not req.text.strip():
                raise HTTPException(status_code=400, detail="Either 'text' or 'turns' must be provided.")
            turns = generate_podcast_script(req.text, language_name=lang_name)

        # Synthesize dual-speaker audio
        podcast_res = synthesize_podcast(turns, language_code=req.target_language_code)
        return {
            "target_language_code": req.target_language_code,
            "turns": turns,
            **podcast_res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-document")
@app.post("/upload-document")
async def api_upload_document(file: UploadFile = File(...)):
    """
    Extracts text from uploaded PDF, TXT, or MD documents.
    """
    try:
        file_bytes = await file.read()
        extracted = extract_text_from_file(file.filename, file_bytes)
        return {
            "filename": file.filename,
            **extracted
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/qa/text")
@app.post("/qa/text")
def api_qa_text(req: QARequest):
    """
    Text-based Q&A Companion: Answers user questions based on the document
    and returns both written answer and spoken voice audio.
    """
    try:
        result = answer_document_question(
            context_text=req.context_text,
            question=req.question,
            language_code=req.language_code
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/qa/voice")
@app.post("/qa/voice")
async def api_qa_voice(
    context_text: str = Form(...),
    language_code: str = Form("hi-IN"),
    file: UploadFile = File(...)
):
    """
    Voice-based Q&A Companion:
    1. Transcribes spoken question using Sarvam Saaras
    2. Answers question based on document using sarvam-105b
    3. Synthesizes voice audio answer using Bulbul
    """
    try:
        audio_bytes = await file.read()
        transcribed_q = transcribe_audio_query(
            audio_bytes=audio_bytes,
            filename=file.filename or "query.wav",
            content_type=file.content_type or "audio/wav"
        )
        if not transcribed_q:
            raise HTTPException(status_code=400, detail="Could not detect speech in the audio recording.")

        result = answer_document_question(
            context_text=context_text,
            question=transcribed_q,
            language_code=language_code
        )
        return {
            "transcribed_question": transcribed_q,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static web frontend if directory exists
STATIC_DIR = Path(__file__).resolve().parent / "static"
PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_frontend():
    if (PUBLIC_DIR / "index.html").exists():
        return FileResponse(str(PUBLIC_DIR / "index.html"))
    if (STATIC_DIR / "index.html").exists():
        return FileResponse(str(STATIC_DIR / "index.html"))
    return JSONResponse({"message": "VaaniSetu API is running"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
