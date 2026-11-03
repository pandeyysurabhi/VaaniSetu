# 🎙️ VaaniSetu (वाणीसेतु) — Indic Audio Intelligence & Accessibility Studio

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg?logo=streamlit)](https://streamlit.io)
[![Sarvam AI](https://img.shields.io/badge/Powered%20By-Sarvam%20AI-orange.svg)](https://www.sarvam.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Empowering 1.4B+ citizens across literacy and language boundaries with expressive Indic audio narration, multi-speaker educational podcasts, and interactive voice companion experiences.**

---

## 🌟 Overview & Societal Impact

India is home to hundreds of millions of citizens who speak regional languages but encounter massive barriers consuming written text — from complex government welfare circulars and legal notices to school textbooks and healthcare advisories. Existing screen readers are monotonous, lack emotional Indic prosody, fail with code-mixed languages, and do not simplify bureaucratic jargon.

**VaaniSetu (वाणीसेतु)** is a full-stack audio intelligence studio powered by **Sarvam AI**:
1. **Expressive Indic Audio Narration** with native prosody across 11 Indic languages.
2. **"Samjhaav" (Citizen Plain-Language Simplifier):** Translating dense legal/bureaucratic circulars into warm, everyday colloquial language.
3. **"NotebookLM for Bharat" (Dual-Speaker Podcasts):** Converting articles and textbooks into a lively 2-host conversational podcast (**Aarav & Meera**).
4. **Interactive Voice & Text Companion:** Hands-free voice question-answering during playback powered by **Saaras (ASR)** and **sarvam-105b**.

---

## 🚀 Key Features

| Feature | Description | Sarvam Engine |
|---|---|---|
| **📖 Direct Narration** | Converts text to natural audio across 11 Indic languages with customizable personas (*Storyteller, News Anchor, Educator, Conversational*) and pacing. | `Bulbul` (`bulbul:v3` / `v4-flash`) |
| **💡 Samjhaav (Citizen Simplifier)** | Automatically eliminates bureaucratic jargon, explaining rights, subsidies, and schemes in plain language. | `sarvam-105b-conversations` |
| **🎙️ NotebookLM for Bharat** | Synthesizes a complete 2-host conversational dialogue (**Host 1: Aarav** & **Host 2: Meera**) stitched into a single podcast MP3 with speech bubble visuals. | `sarvam-105b` + `Bulbul` Multi-Voice |
| **⚡ 60-Second Audio Briefs** | Compresses long articles into high-retention 140-word spoken audio bulletins. | `sarvam-105b` |
| **💬 Voice & Text Companion** | Listeners can ask clarifying questions about the text and receive an instant voice explanation. | `Saaras` (ASR) + `sarvam-105b` + `Bulbul` |
| **📎 PDF & Document Ingestion** | 1-click upload of PDFs, study notes, or government gazettes with automated text extraction. | `pypdf` |

---

## 🌐 Supported Indic Languages

| Language Code | Language Name | Native Script |
|---|---|---|
| `hi-IN` | Hindi | हिन्दी |
| `en-IN` | Indian English | English |
| `bn-IN` | Bengali | বাংলা |
| `ta-IN` | Tamil | தமிழ் |
| `te-IN` | Telugu | తెలుగు |
| `kn-IN` | Kannada | ಕನ್ನಡ |
| `ml-IN` | Malayalam | മലയാളം |
| `mr-IN` | Marathi | मराठी |
| `gu-IN` | Gujarati | ગુજરાતી |
| `pa-IN` | Punjabi | ਪੰਜਾਬੀ |
| `od-IN` | Odia | ଓଡ଼ିଆ |

---

## ☁️ 1-Click Free Deployment on Streamlit Community Cloud

This project is built to deploy on **Streamlit Community Cloud** (100% Free, no timeouts, zero configuration):

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and log in with your GitHub account.
2. Click **"Create app"** -> **"I already have an app"**.
3. Select:
   - **Repository:** `pandeyysurabhi/VaaniSetu`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
4. Expand **Advanced settings** -> **Secrets**, and paste:
   ```toml
   SARVAM_API_KEY = "your_actual_sarvam_api_key_here"
   ```
5. Click **"Deploy"**! 
   Your app will be live with a permanent public link:
   ```
   https://vaanisetu-<your-username>.streamlit.app
   ```

---

## 💻 Local Development

### 1. Clone & Navigate
```bash
git clone https://github.com/pandeyysurabhi/VaaniSetu.git
cd VaaniSetu
```

### 2. Configure `.env`
Create a `.env` file in the project root:
```env
SARVAM_API_KEY=your_sarvam_api_key_here
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Locally
```bash
streamlit run streamlit_app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 🧪 Testing

Run the verification test suite:
```bash
python test_app.py
```

---

## 📜 License
Distributed under the MIT License. Built with ❤️ for Bharat using [Sarvam AI](https://docs.sarvam.ai).
