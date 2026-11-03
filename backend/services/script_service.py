import json
import re
from typing import List, Dict, Any, Optional
from backend.config import get_sarvam_client

def extract_json_from_llm(raw_text: str) -> Any:
    """
    Safely extracts and parses JSON from model output, handling potential markdown fences.
    """
    raw_text = raw_text.strip()
    # Remove markdown code fences if present
    fence_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_text)
    if fence_match:
        raw_text = fence_match.group(1).strip()
    
    # Try direct parse
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # Try finding array or object boundaries
        array_match = re.search(r'\[\s*\{[\s\S]*\}\s*\]', raw_text)
        if array_match:
            return json.loads(array_match.group(0))
        raise ValueError(f"Failed to parse valid JSON from LLM output: {raw_text[:200]}")

def simplify_text(text: str, language_name: str = "Hindi") -> str:
    """
    'Samjhaav' Mode: Rewrites complex bureaucratic, legal, or technical text
    into simple, clear language that any citizen or student can understand.
    """
    client = get_sarvam_client()
    system_prompt = (
        "You are an empathetic, clear Indic public communicator. "
        "Your task is to rewrite the provided text into simple, everyday plain language "
        "so that an ordinary citizen, farmer, or young student can effortlessly understand it. "
        "Eliminate dense jargon, legalese, and bureaucratic phrasing. "
        "Keep the tone warm, clear, and reassuring, while preserving all essential details, benefits, eligibility, and steps. "
        "Output ONLY the rewritten text directly. Do not include any meta-commentary, introductory notes, or disclaimers."
    )
    user_prompt = f"Please rewrite and simplify the following text in clear {language_name}:\n\n{text}"

    response = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.4,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

def summarize_text(text: str, language_name: str = "English", max_words: int = 140) -> str:
    """
    '60-Second Brief': Produces a crisp, high-retention audio brief of the content.
    """
    client = get_sarvam_client()
    system_prompt = (
        "You are an expert audio producer. "
        f"Summarize the provided text into a punchy, engaging 60-second audio bulletin (around {max_words} words). "
        "Focus on the single biggest takeaway and key practical points. "
        "Make it lively and natural to read aloud. "
        "Output ONLY the summary text directly without introductory commentary or titles."
    )
    user_prompt = f"Summarize the following text for a quick audio brief in {language_name}:\n\n{text}"

    response = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.5,
        max_tokens=800
    )
    return response.choices[0].message.content.strip()

def generate_podcast_script(text: str, language_name: str = "Hindi") -> List[Dict[str, str]]:
    """
    'NotebookLM for Bharat': Converts text into a lively 2-host conversational podcast dialogue.
    Host 1 (Aarav): Curious, engaging, asks clarifying questions.
    Host 2 (Meera): Insightful, knowledgeable expert, gives relatable analogies.
    """
    client = get_sarvam_client()
    system_prompt = (
        "You are a podcast script writer for an educational audio show. "
        "Convert the given text into an engaging, natural conversation between two hosts: "
        "Host 1 ('host1' - Aarav, curious and energetic, asks great questions) and "
        "Host 2 ('host2' - Meera, wise expert, explains concepts with relatable analogies). "
        "The dialogue should sound natural and spoken, not robotic. "
        "You must output ONLY a valid JSON array of objects with keys: "
        "'speaker' ('host1' or 'host2') and 'text' (the dialogue line). "
        "Produce between 4 to 6 dialogue turns. Do not include markdown formatting or extra text."
    )
    user_prompt = f"Convert this text into a 2-host podcast dialogue in {language_name}:\n\n{text}"

    response = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1200
    )
    raw = response.choices[0].message.content
    return extract_json_from_llm(raw)

