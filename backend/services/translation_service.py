import re
from typing import Optional, List, Dict
from backend.config import get_sarvam_client, SUPPORTED_LANGUAGES

def split_text_into_chunks(text: str, max_chars: int = 850) -> List[str]:
    """
    Split text into chunks of at most max_chars without breaking mid-sentence.
    Preserves paragraphs and sentences cleanly.
    """
    if len(text) <= max_chars:
        return [text]

    # Split by paragraphs first
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # If single paragraph exceeds max_chars, split by sentences
        if len(para) > max_chars:
            sentences = re.split(r'(?<=[.!?।])\s+', para)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                if len(current_chunk) + len(sentence) + 1 <= max_chars:
                    current_chunk = f"{current_chunk} {sentence}".strip()
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    # If a single sentence is still larger than max_chars, split by punctuation or words
                    if len(sentence) > max_chars:
                        words = sentence.split()
                        sub_chunk = ""
                        for word in words:
                            if len(sub_chunk) + len(word) + 1 <= max_chars:
                                sub_chunk = f"{sub_chunk} {word}".strip()
                            else:
                                if sub_chunk:
                                    chunks.append(sub_chunk)
                                sub_chunk = word
                        if sub_chunk:
                            current_chunk = sub_chunk
                        else:
                            current_chunk = ""
                    else:
                        current_chunk = sentence
        else:
            if len(current_chunk) + len(para) + 2 <= max_chars:
                current_chunk = f"{current_chunk}\n\n{para}".strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def detect_language(text: str) -> Dict[str, str]:
    """
    Identifies the language and script of the input text using Sarvam's language identifier.
    """
    client = get_sarvam_client()
    sample_text = text[:500] if len(text) > 500 else text
    response = client.text.identify_language(input=sample_text)
    lang_code = response.language_code
    return {
        "language_code": lang_code,
        "script_code": response.script_code,
        "language_name": SUPPORTED_LANGUAGES.get(lang_code, {}).get("name", lang_code)
    }

def translate_text(
    text: str,
    target_language_code: str,
    source_language_code: str = "auto",
    mode: str = "formal",
    model: str = "mayura:v1"
) -> Dict[str, str]:
    """
    Translates text to the target Indic language, handling long texts via chunking.
    """
    if not text.strip():
        return {"translated_text": "", "source_language_code": source_language_code}

    # If source and target are the same, no translation needed
    if source_language_code != "auto" and source_language_code == target_language_code:
        return {"translated_text": text, "source_language_code": source_language_code}

    client = get_sarvam_client()
    chunks = split_text_into_chunks(text, max_chars=850)
    translated_chunks = []
    detected_source = source_language_code

    for chunk in chunks:
        resp = client.text.translate(
            input=chunk,
            source_language_code=source_language_code,
            target_language_code=target_language_code,
            mode=mode,
            model=model
        )
        translated_chunks.append(resp.translated_text)
        if resp.source_language_code and detected_source == "auto":
            detected_source = resp.source_language_code

    full_translated_text = " ".join(translated_chunks)
    return {
        "translated_text": full_translated_text,
        "source_language_code": detected_source
    }

