import io
import sys
import unittest
import base64
from fastapi.testclient import TestClient

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from backend.app import app
from backend.config import get_sarvam_client

client = TestClient(app)

class TestPhase3(unittest.TestCase):
    def test_qa_text(self):
        context = (
            "The PM Kisan Samman Nidhi provides Rs 6,000 per year to eligible farmer families. "
            "The funds are released in three equal installments of Rs 2,000 every four months."
        )
        question = "How much money do farmers get in each installment?"
        resp = client.post("/api/qa/text", json={
            "context_text": context,
            "question": question,
            "language_code": "en-IN"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("answer_text", data)
        self.assertIn("audio_base64", data)
        self.assertTrue(len(data["audio_base64"]) > 500)
        print("[PASS] /api/qa/text verified: Answered question and generated voice audio.")

    def test_qa_voice(self):
        # Generate a voice query audio using Bulbul to simulate a real user's spoken voice
        sarvam = get_sarvam_client()
        tts_query = sarvam.text_to_speech.convert(
            text="How much total money is provided per year?",
            language_code="en-IN",
            speaker="aditya",
            output_audio_codec="wav"
        )
        wav_bytes = base64.b64decode(tts_query.audios[0])

        context = "The PM Kisan Samman Nidhi provides Rs 6,000 per year to eligible farmer families."
        resp = client.post(
            "/api/qa/voice",
            data={
                "context_text": context,
                "language_code": "en-IN"
            },
            files={"file": ("query.wav", io.BytesIO(wav_bytes), "audio/wav")}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("transcribed_question", data)
        self.assertIn("answer_text", data)
        self.assertIn("audio_base64", data)
        print(f"[PASS] /api/qa/voice verified: Saaras transcribed '{data['transcribed_question']}' and answered with voice.")

if __name__ == "__main__":
    unittest.main()

