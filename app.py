import streamlit as st
from src.pdf_parser import extract_text_from_pdf
from src.interview_engine import analyze_resume_and_jd, evaluate_answer, generate_final_report
from src.voice_utils import text_to_speech, speech_to_text

st.set_page_config(page_title="HireReady AI — Mock Interviewer", page_icon="🎯", layout="wide")

if "stage" not in st.session_state:
    st.session_state.stage = "setup"
if "interview_mode" not in st.session_state:
    st.session_state.interview_mode = "💬 Text Interview (Type Answers)"
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""
if "ats_result" not in st.session_state:
    st.session_state.ats_result = {}
if "messages" not in st.session_state:
    st.session_state.messages = []
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []
if "current_question" not in st.session_state:
    st.session_state.current_question = ""
if "question_number" not in st.session_state:
    st.session_state.question_number = 1
if "final_report" not in st.session_state:
    st.session_state.final_report = ""
if "spoken_q_num" not in st.session_state:
    st.session_state.spoken_q_num = 0

TOTAL_QUESTIONS = 5


def reset_interview():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


with st.sidebar:
    st.title("🎯 HireReady AI")
    st.caption("ATS Gap Analyzer & AI Mock Interviewer")
    st.markdown("---")
    if st.session_state.stage != "setup":
        st.info(f"**Mode:** {st.session_state.interview_mode}")
        st.metric("ATS Match Score", f"{st.session_state.ats_result.get('match_score', 0)}%")
        completed = min(st.session_state.question_number - 1, TOTAL_QUESTIONS)
        st.progress(completed / TOTAL_QUESTIONS)
        st.write(f"**Progress:** {completed} / {TOTAL_QUESTIONS} Questions")
        st.markdown("---")
        if st.button("🔄 Start New Interview", use_container_width=True):
            reset_interview()
    else:
        st.info(
            "**How It Works:**\n"
            "1. Upload your Resume in PDF format.\n"
            "2. Paste the target Job Description.\n"
            "3. Choose Text or Voice Assistant mode to begin."
        )


if st.session_state.stage == "setup":
    st.title("🎯 HireReady AI — Smart Mock Interviewer")
    selected_mode = st.radio(
        "1️⃣ Select Interview Mode:",
        ["💬 Text Interview (Type Answers)", "🎙️ AI Voice Assistant (Speak Answers)"],
        horizontal=True
    )
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        uploaded_pdf = st.file_uploader("2️⃣ Upload Resume (PDF):", type=["pdf"])
    with col2:
        jd_input = st.text_area(
            "3️⃣ Paste Job Description (JD):",
            height=200,
            placeholder="Paste the job requirements, skills, and role description here..."
        )

    if st.button("🚀 Analyze Resume & Start Interview", type="primary", use_container_width=True):
        if not uploaded_pdf or not jd_input.strip():
            st.warning("⚠️ Please upload your Resume PDF and paste the Job Description before starting!")
        else:
            try:
                with st.spinner("📄 Extracting text from Resume PDF..."):
                    resume_text = extract_text_from_pdf(uploaded_pdf)
                with st.spinner("🧠 Running ATS Gap Analysis & preparing questions..."):
                    ats_data = analyze_resume_and_jd(resume_text, jd_input.strip())

                st.session_state.interview_mode = selected_mode
                st.session_state.resume_text = resume_text
                st.session_state.jd_text = jd_input.strip()
                st.session_state.ats_result = ats_data
                first_q = ats_data.get("first_question", "Tell me about your most challenging technical project.")
                st.session_state.current_question = first_q
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"**Question 1 of {TOTAL_QUESTIONS}:**\n\n{first_q}"
                })
                st.session_state.stage = "interview"
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


elif st.session_state.stage == "interview":
    is_voice_mode = "Voice" in st.session_state.interview_mode
    st.title("🎙️ AI Voice Technical Interview" if is_voice_mode else "💬 AI Text Technical Interview")

    with st.expander("📊 ATS Gap Analysis Report", expanded=False):
        ats = st.session_state.ats_result
        c1, c2, c3 = st.columns(3)
        c1.metric("ATS Match Score", f"{ats.get('match_score', 0)} / 100")
        c2.success("**✅ Strengths:**\n" + ", ".join(ats.get("matching_strengths", [])))
        c3.error("**⚠️ Missing Skills:**\n" + ", ".join(ats.get("missing_skills", [])))

    st.markdown("---")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_answer = None

    if is_voice_mode:
        if st.session_state.current_question:
            try:
                audio_bytes = text_to_speech(st.session_state.current_question)
                autoplay = st.session_state.spoken_q_num != st.session_state.question_number
                st.audio(audio_bytes, format="audio/mp3", autoplay=autoplay)
                st.session_state.spoken_q_num = st.session_state.question_number
            except Exception as e:
                st.caption(f"🔇 Audio unavailable: {str(e)}")

        audio_rec = st.audio_input(
            f"🎤 Click the mic to speak your answer for Question {st.session_state.question_number}:",
            key=f"mic_{st.session_state.question_number}"
        )
        if audio_rec:
            with st.spinner("🎧 Transcribing your voice response..."):
                try:
                    user_answer = speech_to_text(audio_rec.getvalue())
                except Exception as e:
                    st.error(f"❌ Voice Transcription Error: {str(e)}")
    else:
        user_answer = st.chat_input("Type your technical answer here and press Enter...")

    if user_answer:
        st.session_state.messages.append({"role": "user", "content": user_answer})
        with st.chat_message("user"):
            st.markdown(user_answer)

        with st.chat_message("assistant"):
            with st.spinner("🤔 Evaluating your answer..."):
                try:
                    eval_data = evaluate_answer(
                        st.session_state.resume_text,
                        st.session_state.jd_text,
                        st.session_state.current_question,
                        user_answer,
                        st.session_state.question_number,
                        TOTAL_QUESTIONS
                    )
                    score = eval_data.get("score") or eval_data.get("Score", 5)
                    feedback = eval_data.get("feedback") or eval_data.get("Feedback", "")
                    next_q = eval_data.get("next_question") or eval_data.get("Next_question", "")

                    st.session_state.qa_history.append({
                        "question": st.session_state.current_question,
                        "answer": user_answer,
                        "score": score,
                        "feedback": feedback
                    })

                    if st.session_state.question_number >= TOTAL_QUESTIONS or not next_q:
                        st.session_state.question_number += 1
                        with st.spinner("📋 Generating Final Readiness Scorecard..."):
                            report = generate_final_report(
                                st.session_state.resume_text,
                                st.session_state.jd_text,
                                st.session_state.qa_history
                            )
                            st.session_state.final_report = report
                            st.session_state.stage = "completed"
                            st.rerun()
                    else:
                        st.session_state.question_number += 1
                        st.session_state.current_question = next_q
                        bot_reply = (
                            f"**Score: {score}/10** | 💡 *Feedback:* {feedback}\n\n"
                            f"---\n"
                            f"**Question {st.session_state.question_number} of {TOTAL_QUESTIONS}:**\n\n{next_q}"
                        )
                        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Evaluation Error: {str(e)}")


elif st.session_state.stage == "completed":
    st.title("🏆 Final Interview Readiness Scorecard")
    scores = [item.get("score") or item.get("Score", 0) for item in st.session_state.qa_history]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("ATS Resume Match", f"{st.session_state.ats_result.get('match_score', 0)}%")
    col2.metric("Average Score", f"{avg_score} / 10")
    col3.metric("Questions Answered", f"{len(scores)} / {TOTAL_QUESTIONS}")

    st.markdown("---")
    st.markdown(st.session_state.final_report)
    st.download_button(
        "📥 Download Readiness Report (.md)",
        st.session_state.final_report,
        "HireReady_Scorecard.md",
        "text/markdown",
        type="primary"
    )

    with st.expander("🔍 View Question-by-Question Breakdown"):
        for idx, item in enumerate(st.session_state.qa_history, 1):
            st.markdown(f"**Q{idx}: {item.get('question', '')}**")
            st.write(f"- **Your Answer:** {item.get('answer', '')}")
            st.write(f"- **Score:** {item.get('score', 0)}/10 | **Feedback:** {item.get('feedback', '')}")
