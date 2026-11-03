import sys
import unittest

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from backend.config import get_sarvam_client, SUPPORTED_LANGUAGES, VOICE_PERSONAS
from backend.services.tts_service import synthesize_speech
from backend.services.translation_service import translate_text, detect_language
from backend.services.script_service import simplify_text, summarize_text
from backend.services.document_service import extract_text_from_file

class TestStreamlitServices(unittest.TestCase):
    def test_client_and_config(self):
        client = get_sarvam_client()
        self.assertIsNotNone(client)
        self.assertIn("hi-IN", SUPPORTED_LANGUAGES)
        self.assertIn("storyteller", VOICE_PERSONAS)
        print("[PASS] Sarvam client and configurations verified.")

    def test_translation_and_detect(self):
        det = detect_language("नमस्ते, आप कैसे हैं?")
        self.assertEqual(det["language_code"], "hi-IN")
        
        trans = translate_text("Hello, welcome to India.", target_language_code="hi-IN", source_language_code="en-IN")
        self.assertTrue(len(trans["translated_text"]) > 0)
        print("[PASS] Language detection and translation verified.")

    def test_tts(self):
        res = synthesize_speech("वाणीसेतु में आपका स्वागत है।", language_code="hi-IN", speaker="roopa")
        self.assertIn("audio_base64", res)
        self.assertTrue(len(res["audio_base64"]) > 1000)
        print("[PASS] Bulbul TTS speech synthesis verified.")

    def test_document_extraction(self):
        sample_bytes = b"# Sample Circular\n\nFinancial assistance announced."
        res = extract_text_from_file("circular.md", sample_bytes)
        self.assertIn("Sample Circular", res["text"])
        print("[PASS] Document extraction verified.")

if __name__ == "__main__":
    unittest.main()

