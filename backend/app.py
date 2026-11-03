import os
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from backend.config import SUPPORTED_LANGUAGES, VOICE_PERSONAS, SARVAM_API_KEY
from backend.services.tts_service import synthesize_speech
from backend.services.translation_service import translate_text, detect_language

app = FastAPI(
    title="VaaniSetu (वाणीसेतु) API",
    description="Indic Audio Intelligence & Accessibility Platform powered by Sarvam AI",
    version="1.0.0"
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

# Endpoints
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "VaaniSetu Audio Intelligence",
        "sarvam_configured": bool(SARVAM_API_KEY),
        "version": "1.0.0"
    }

@app.get("/api/languages")
def get_languages():
    return {"languages": SUPPORTED_LANGUAGES}

@app.get("/api/personas")
def get_personas():
    return {"personas": VOICE_PERSONAS}

@app.post("/api/detect-language")
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
def api_narrate(req: NarrationRequest):
    """
    Combined pipeline:
    1. Detects language if auto
    2. Translates if target language differs from source
    3. Synthesizes expressive audio using chosen persona
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    try:
        # Step 1 & 2: Translate if necessary
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

        # Step 3: Synthesize audio
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

# Mount static web frontend if directory exists
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    def serve_frontend():
        return FileResponse(str(STATIC_DIR / "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
