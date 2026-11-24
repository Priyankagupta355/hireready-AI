
# 🎯 HireReady AI — ATS Gap Analyzer & AI Voice Mock Interviewer

An end-to-end **Stateful AI Mock Interviewer & Resume ATS Analyzer** built with **Python, Streamlit, and Groq LLM + Whisper APIs**. Candidates can upload their Resume PDF, paste a target Job Description, and take a real-time technical interview via **Text Chat** or **AI Voice Assistant**.

## ✨ Key Features

- **ATS Gap Analysis:** Calculates resume-to-JD match score, identifies matching strengths, and highlights missing skills.
- **Dual Interview Modes:** Switch between **Text Chat Mode** and **AI Voice Assistant Mode** (Text-to-Speech questions + Groq Whisper Speech-to-Text answers).
- **Real-Time Answer Evaluation:** Scores every answer (1–10) with actionable feedback and adapts follow-up questions.
- **Final Readiness Scorecard:** Generates a comprehensive Markdown hiring report with a 3-day study plan.

## 🛠️ Tech Stack

- **Frontend & State Management:** Streamlit (`st.session_state`, `st.audio_input`)
- **LLM & Speech-to-Text:** Groq API (`openai/gpt-oss-120b` & `whisper-large-v3-turbo`)
- **Text-to-Speech:** gTTS
- **Document Parsing:** PyPDF

## ⚙️ Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com
   cd hireready-ai
   ```
