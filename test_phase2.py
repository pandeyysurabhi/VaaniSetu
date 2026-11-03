import sys
import unittest
import io
from fastapi.testclient import TestClient

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from backend.app import app

client = TestClient(app)

class TestPhase2(unittest.TestCase):
    def test_adapt_simplify(self):
        sample = (
            "Pursuant to statutory notification S.O. 123(E), beneficiaries categorized "
            "as marginalized agriculturalists must submit biometric de-duplication affidavits."
        )
        resp = client.post("/api/adapt", json={
            "text": sample,
            "mode": "simplify",
            "target_language_code": "hi-IN"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("adapted_text", data)
        self.assertTrue(len(data["adapted_text"]) > 10)
        print("[PASS] /api/adapt (simplify) verified: Simplified text generated in", data["language"])

    def test_adapt_summary(self):
        sample = (
            "The Indian government has launched the National Green Hydrogen Mission with an outlay "
            "of Rs 19,744 crore to promote commercial production and make India an export hub for clean fuel."
        )
        resp = client.post("/api/adapt", json={
            "text": sample,
            "mode": "summary",
            "target_language_code": "en-IN"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("adapted_text", data)
        self.assertTrue(len(data["adapted_text"]) > 10)
        print("[PASS] /api/adapt (summary) verified: 60-second summary generated.")

    def test_adapt_podcast_script(self):
        sample = "ISRO successfully launched the Chandrayaan mission to explore water ice in the Moon's south pole."
        resp = client.post("/api/adapt", json={
            "text": sample,
            "mode": "podcast",
            "target_language_code": "en-IN"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("turns", data)
        self.assertTrue(len(data["turns"]) >= 2)
        print("[PASS] /api/adapt (podcast) verified: Generated", len(data["turns"]), "dialogue turns.")

    def test_podcast_synthesis(self):
        turns = [
            {"speaker": "host1", "text": "Welcome to our science podcast! Did you hear about the new solar mission?"},
            {"speaker": "host2", "text": "Yes Aarav, it will help us understand solar flares and protect satellites."}
        ]
        resp = client.post("/api/podcast", json={
            "turns": turns,
            "target_language_code": "en-IN"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("audio_base64", data)
        self.assertEqual(data["turn_count"], 2)
        self.assertTrue(len(data["audio_base64"]) > 1000)
        print("[PASS] /api/podcast verified: Multi-speaker podcast audio synthesized successfully.")

    def test_upload_document_text(self):
        dummy_content = b"# Tribal Healthcare Bulletin\n\nMobile clinics have commenced operations."
        file_obj = io.BytesIO(dummy_content)
        resp = client.post(
            "/api/upload-document",
            files={"file": ("bulletin.md", file_obj, "text/markdown")}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["filename"], "bulletin.md")
        self.assertIn("Tribal Healthcare Bulletin", data["text"])
        print("[PASS] /api/upload-document verified: Extracted markdown/text file.")

if __name__ == "__main__":
    unittest.main()

