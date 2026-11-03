# Project Specification: VaaniSetu (वाणीसेतु) — Indic Audio Intelligence & Accessibility Studio

---

## 1. Executive Summary

**VaaniSetu (वाणीसेतु)** is an AI-powered multimodal audio studio and accessibility platform built on Sarvam AI. It bridges the literacy, language, and accessibility divide in India by converting written text, documents, textbooks, and government notifications into natural, expressive, multi-speaker Indic audio narration, conversational podcasts, and interactive voice experiences.

By coupling Sarvam's state-of-the-art models (**Bulbul** for TTS, **Mayura** for translation, **Saaras** for speech recognition, **DocAI** for document parsing, and **sarvam-105b** for language understanding and dialogue generation), VaaniSetu transforms dense, mono-lingual written material into engaging, localized, and easily digestible audio formats.

---

## 2. Problem Statement & Societal Impact

### The Challenge
- **Literacy & Language Barriers:** India has over 1.4 billion citizens speaking 22+ official languages. Hundreds of millions face literacy or visual challenges, leaving them unable to consume written text such as news, government welfare schemes, school textbooks, and health circulars.
- **Robotic Screen Readers:** Existing screen readers are monotonous, lack emotional prosody for Indian languages, fail with colloquial code-mixed text (Hinglish, Tanglish), and do not simplify complex bureaucratic or academic jargon.
- **Content Repurposing Overhead:** Content creators, educators, and organizations lack automated tools to produce localized regional-language audio (podcasts, educational explainers, audiobooks) cost-effectively.

### Target Audience & Real-World Impact
1. **Visually Impaired & Senior Citizens:** Accessible, natural-sounding audio reader with real-time speed control, pitch tuning, and voice customization.
2. **Rural & Semi-Urban Populations:** Simplifying government schemes (e.g., PM-Kisan, DBT, Ayushman Bharat) into clear, spoken regional dialects shareable via WhatsApp.
3. **Students & Competitive Exam Aspirants (UPSC/State Boards):** Turning dense PDF notes and textbooks into educational audio summaries and dual-host study podcasts.
4. **Independent Creators & Publishers:** 1-click generation of localized audio versions for blogs, newsletters, and articles.

---

## 3. Core Feature Architecture

### Feature Pillar 1: Multimodal Ingestion Engine
- **Direct Text & Markdown:** Paste blogs, news articles, or raw text.
- **Document & PDF Upload (Sarvam DocAI):** Extract clean, formatted text from scanned PDFs, book pages, circulars, and notices without header/footer noise.
- **Webpage & URL Reader:** Scrape article body text directly from blog or news links.

### Feature Pillar 2: Content Adaptation Studio (`sarvam-105b`)
Before feeding text to the TTS engine, `sarvam-105b` transforms the content according to the user's chosen persona/mode:
1. **Verbatim Reader Mode:** Exact text narration with intelligent pronunciation enhancements for numbers, abbreviations, and Indian acronyms.
2. **Samjhaav (Simplify / Plain Language):** Rewrites legal, bureaucratic, or medical jargon into clear, everyday language suitable for common citizens.
3. **Podcast / Dialogue Mode (NotebookLM for Bharat):** Automatically rewrites articles into a lively, 2-speaker conversation (Host & Expert) discussing key takeaways.
4. **Summary & Bullet Audio:** 60-second audio brief covering the core highlights.

### Feature Pillar 3: Indic Audio Narration Engine (`Bulbul` + `Mayura`)
- **Multilingual Translation (`Mayura`):** Translate source content into Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, Gujarati, Malayalam, Odia, Punjabi, and Indian English.
- **Emotion & Tone Modulation:**
  - *News Anchor:* Authoritative, brisk pacing, crisp diction.
  - *Storyteller / Kathakar:* Warm, expressive, modulated pauses for engagement.
  - *Teacher / Explainer:* Patient, structured cadence.
- **Instant Voice Personalization (Voice Cloning API):** Allows users or educators to clone a custom voice from a short reference audio clip (e.g., student studying with a familiar teacher's voice).
- **Audio Soundstaging:** Optional subtle intro/outro music and ambient beds for studio-grade polish.

### Feature Pillar 4: Interactive Audio Player & Voice Companion
- **Synchronized Karaoke Transcript:** Highlight sentences in real time as the audio plays.
- **Voice-Activated Q&A (`Saaras` + `sarvam-105b-conversations`):** Listeners can pause the audio and speak questions (e.g., *"Yeh yojana kiske liye hai?"*), receiving immediate voice clarification.
- **Export & WhatsApp Distribution:** 1-click download as MP3/WAV, optimized low-bandwidth audio export for rural networks, and instant WhatsApp-ready audio cards.

---

## 4. Sarvam AI Technology Mapping

| Platform Capability | Sarvam API / Model | Purpose in VaaniSetu |
|---|---|---|
| **Text Transformation & Scripting** | `sarvam-105b` | Rewrites input into podcast scripts, summaries, and simplified Indic language |
| **Conversational Voice Q&A** | `sarvam-105b-conversations` | Powers the real-time audio companion for question-answering during playback |
| **Text-to-Speech (TTS)** | `Bulbul` (`bulbul:v1` / `v4`) | Generates expressive Indic speech across 10+ languages with diverse speakers |
| **Voice Cloning** | Sarvam Voice Cloning API | Clones custom voice profiles from user-provided audio samples |
| **Language Translation** | `Mayura` (`sarvam-translate`) | High-accuracy Indic-to-Indic and English-to-Indic translation |
| **Voice Commands & Query Input** | `Saaras` (`speech-to-text`) | Transcribes user voice questions and playback control commands |
| **Document Digitization** | Sarvam DocAI / Vision | Extracts structural text from scanned PDFs, circulars, and textbooks |

---

## 5. Technology Stack & Deployment Plan

### Tech Stack
- **Backend:** Python (FastAPI) — clean REST endpoints, streaming audio responses, async job processing.
- **Frontend:** Modern responsive web interface (Vite + React or modern Tailwind SPA) with custom HTML5 audio visualization and sentence highlighting.
- **Client SDK:** Official `sarvamai` Python SDK.
- **State & Storage:** Local cache for synthesized audio chunks; zero persistent credential storage (reads from `.env`).

### Deployment Strategy (Bonus Points)
- **Containerization:** Production-ready `Dockerfile` and `docker-compose.yml`.
- **Target Platforms:**
  - **Option A (Hugging Face Spaces):** Free hosting with instant public URL and direct audio widget rendering.
  - **Option B (Render / Railway):** Free/standard cloud deployment with automated CI/CD from GitHub (`pandeyysurabhi/sarvam`).
  - **Option C (Vercel / Fly.io):** Containerized serverless deployment.

---

## 6. Implementation Roadmap

```
Phase 1: Foundation (Hours 1 - 2)
  ├── Setup FastAPI backend structure & configuration
  ├── Implement core TTS synthesis service (Bulbul) with voice & pace selection
  └── Implement translation pipeline (Mayura)

Phase 2: Content Adaptation Studio (Hours 2 - 4)
  ├── Integrate sarvam-105b for script writing (Simplify, Podcast Dialogue, Summary)
  ├── Multi-speaker TTS generator (interleaving speaker tracks into a single audio file)
  └── Document text extraction integration (DocAI / PDF Parser)

Phase 3: Interactive UI & Player (Hours 4 - 6)
  ├── Build intuitive web dashboard for input selection (Text / PDF / URL)
  ├── Build custom player with playback speed, sentence karaoke, and language switcher
  └── Add Voice Q&A companion modal (Saaras + sarvam-105b-conversations)

Phase 4: Polish, WhatsApp Audio Export & Deployment (Hours 6 - 8)
  ├── MP3 compression and WhatsApp share optimization
  ├── Containerize application (Dockerfile)
  ├── Deploy to live cloud URL (Render / Hugging Face Spaces)
  └── Complete documentation and push to GitHub repository
```

---

## 7. Success & Impact Metrics
- **Synthesis Speed:** Under 3 seconds for 1-minute audio segments.
- **Language Coverage:** 10+ Indian languages (Hindi, Tamil, Telugu, Bengali, Marathi, etc.) + Indian English.
- **Engagement Multiplier:** Dual-speaker dialogue format boosts retention by 3x compared to flat text readers.
- **Accessibility Score:** 100% keyboard and voice-navigable interface.

