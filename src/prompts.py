def get_ats_analysis_prompt(resume_text: str, jd_text: str) -> str:
    """
    A prompt to compare a Resume and a Job Description to generate 
    an ATS Match Score, Missing Skills, and the First Interview Question.
    """
    return f"""
    You are an expert Technical Recruiter and Senior Engineering Hiring Manager.
    Analyze the candidate's Resume against the provided Job Description (JD).
    
    **Candidate Resume:**
    {resume_text}

    **Job Description:**
    {jd_text}

    **Task:**
    1. Calculate a realistic ATS Match Score (0 to 100) based on skills, projects, and role alignment.
    2. Identify key skills/keywords present in the JD that are missing or weak in the Resume.
    3. Highlight the candidate's top matching strengths.
    4. Formulate the **First Interview Question (Question 1)** tailored specifically to their resume projects and the JD requirements.

    **Strict Output Format:**
    Return ONLY a valid JSON object with the exact keys shown below (no markdown formatting, no extra text):
    {{
        "match_score": 75,
        "matching_strengths": ["Python", "REST APIs", "Project X"],
        "missing_skills": ["Docker", "AWS", "System Design"],
        "short_summary": "2-line recruiter verdict on candidate fit.",
        "first_question": "Your tailored opening technical interview question here."    
    }}
    """


def get_answer_evaluation_prompt(
        resume_text: str,
        jd_text: str,
        question: str,
        user_answer: str,
        question_answer: int,
        total_questions: int = 5
) -> str:
    """
    It scores the candidate's answer 
    from 1 to 10, gives constructive feedback, and generates the next question if the interview is still ongoing.
    """   

    is_last_question = (question_answer >= total_questions)

    next_q_instruction = (
        'Set "next_question" to "" (empty string) because this was the final question.' 
        if is_last_question
        else f'Generate Question {question_answer + 1} of {total_questions}: Ask a relevant follow-up or a new technical/behavioral question based on the Resume and JD (avoid repeating previous topics).'

    ) 

    return f"""
    You are a Senior Technical Interviewer conducting a real-time mock interview.
    Evaluate the candidate's answer objectively and continue the interview naturally.
    
    **Context:**
    - Job Description Summary: {jd_text[:1000]}
    - Candidate Resume Summary: {resume_text[:1000]}
    - Question Asked (Q{question_answer}/{total_questions}): {question}
    - Candidate's Answer: {user_answer}

    **Task:**
    1. Score the answer from 1 to 10 (be fair and realistic; 1-4 = weak/off-topic, 5-7 = average/partially correct, 8-10 = strong/detailed with examples).
    2. Provide concise, actionable feedback (2-3 lines) on what was good and what was missing in their answer.
    3. {next_q_instruction}

    
    **Strict Output Format:**
    Return ONLY a valid JSON object with these exact keys:
    {{
        "score": 7,
        "feedback": "Your explanations of X was clear, but you missed mentioning Y.",
        "next_question": "Your next interview question here (or empty string if final question)."
    }}
    """

def get_final_report_prompt(resume_text: str, jd_text: str, qa_history: list) -> str:
    """
    Poore interview ke Q&A history aur scores ke aadhar par ek detailed
    Final Readiness Scorecard Report (Markdown me) generate karta hai.
    """
    formatted_history = ""
    for idx, item in enumerate(qa_history, 1):
        q_text = item.get('question') or item.get('Question', '')
        ans_text = item.get('answer') or item.get('Answer', '')
        score_val = item.get('score') or item.get('Score', 'N/A')
        fb_text = item.get('feedback') or item.get('Feedback', '')

        formatted_history += f"""
        Q{idx}: {q_text}
        Candidate Answer: {ans_text}
        Score: {score_val}/10
        Feedback: {fb_text}
        ---
        """

    return f"""
    You are a Hiring Committee Lead. Based on the mock interview transcript below, write a comprehensive **Final Interview Readiness Report** for the candidate.

    **Interview Transcript & Scores:**
    {formatted_history}

    **Job Description Context:**
    {jd_text[:800]}

    **Generate a well-structured Markdown Report covering:**
    1. **Overall Readiness Verdict:** (e.g., Strong Hire / Ready with Minor Prep / Needs Practice) & Average Score.
    2. **Key Strengths Demonstrated:** Bullet points of concepts they answered well.
    3. **Areas for Improvement:** Specific technical or communication gaps noticed during the interview.
    4. **3-Day Actionable Study Plan:** Concrete topics/resources they should revise before the actual interview.

    Keep the tone encouraging, honest, and practical.
    """
