import io
import re
from typing import Dict, Any
from pypdf import PdfReader

def extract_text_from_pdf(pdf_bytes: bytes, max_pages: int = 15) -> Dict[str, Any]:
    """
    Extracts and normalizes clean readable text from a PDF file.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    total_pages = len(reader.pages)
    pages_to_read = min(total_pages, max_pages)

    extracted_pages = []
    for i in range(pages_to_read):
        page_text = reader.pages[i].extract_text() or ""
        # Clean up common PDF artifact patterns (excess whitespace, hyphenation)
        cleaned = re.sub(r'(\w+)-\n(\w+)', r'\1\2', page_text)
        cleaned = re.sub(r'\n{2,}', '\n\n', cleaned)
        cleaned = cleaned.strip()
        if cleaned:
            extracted_pages.append(cleaned)

    full_text = "\n\n".join(extracted_pages)
    return {
        "text": full_text,
        "total_pages": total_pages,
        "processed_pages": pages_to_read,
        "char_count": len(full_text)
    }

def extract_text_from_file(filename: str, file_bytes: bytes) -> Dict[str, Any]:
    """
    Router for document extraction based on extension.
    """
    fn_lower = filename.lower()
    if fn_lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif fn_lower.endswith((".txt", ".md", ".csv")):
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = file_bytes.decode("latin-1")
        return {
            "text": text.strip(),
            "total_pages": 1,
            "processed_pages": 1,
            "char_count": len(text)
        }
    else:
        raise ValueError("Unsupported file type. Please upload a PDF, TXT, or MD document.")

