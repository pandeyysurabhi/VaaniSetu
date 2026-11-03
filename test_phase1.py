import sys
import unittest
from fastapi.testclient import TestClient

# Ensure UTF-8 output
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from backend.app import app

client = TestClient(app)

class TestPhase1(unittest.TestCase):
    def test_health(self):
        resp = client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["sarvam_configured"])
        print("[PASS] /api/health verified.")

    def test_languages(self):
        resp = client.get("/api/languages")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("hi-IN", data["languages"])
        self.assertIn("en-IN", data["languages"])
        self.assertIn("ta-IN", data["languages"])
        print("[PASS] /api/languages verified with", len(data["languages"]), "languages.")

    def test_personas(self):
        resp = client.get("/api/personas")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("storyteller", data["personas"])
        self.assertIn("news", data["personas"])
        print("[PASS] /api/personas verified.")

    def test_detect_language(self):
        sample = "नमस्ते, आप कैसे हैं?"
        resp = client.post("/api/detect-language", json={"text": sample})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["language_code"], "hi-IN")
        print("[PASS] /api/detect-language verified: detected", data["language_code"])

    def test_translate(self):
        sample = "Good morning and welcome to the national summit."
        resp = client.post("/api/translate", json={
            "text": sample,
            "source_language_code": "en-IN",
            "target_language_code": "hi-IN"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(len(data["translated_text"]) > 0)
        print("[PASS] /api/translate verified: translated to", data["translated_text"])

    def test_tts(self):
        sample = "वाणीसेतु में आपका स्वागत है।"
        resp = client.post("/api/tts", json={
            "text": sample,
            "language_code": "hi-IN",
            "speaker": "roopa",
            "pace": 1.0
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(len(data["audio_base64"]) > 1000)
        print("[PASS] /api/tts verified: audio base64 generated, length =", len(data["audio_base64"]))

    def test_narrate_pipeline(self):
        sample = "The Ministry of Agriculture has rolled out a major initiative for organic farming in tribal regions."
        resp = client.post("/api/narrate", json={
            "text": sample,
            "source_language_code": "en-IN",
            "target_language_code": "hi-IN",
            "persona": "news",
            "pace": 1.0
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("audio_base64", data)
        self.assertIn("translated_text", data)
        self.assertTrue(len(data["audio_base64"]) > 1000)
        print("[PASS] /api/narrate pipeline verified: End-to-end translation + TTS succeeded.")

if __name__ == "__main__":
    unittest.main()

