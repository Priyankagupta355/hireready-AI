import os
import json
from dotenv import load_dotenv
from groq import Groq
from src.prompts import (
    get_ats_analysis_prompt,
    get_answer_evaluation_prompt,
    get_final_report_prompt
)

load_dotenv(override=True)

def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY nahi mili! Kripya .env file check karein.")
    return Groq(api_key=api_key)


def analyze_resume_and_jd(resume_text: str, jd_text: str) -> dict:
    """
    Layer 2: Resume aur JD ka ATS Gap Analysis karta hai aur pehla sawal banata hai.
    """
    client = get_groq_client()
    prompt = get_ats_analysis_prompt(resume_text, jd_text)

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            reasoning_format="hidden",
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise Exception(f"ATS Analysis me error aaya: {str(e)}")


def evaluate_answer(
    resume_text: str,
    jd_text: str,
    question: str,
    user_answer: str,
    question_number: int,
    total_questions: int = 5
) -> dict:
    """
    Layer 4: User ke jawab ko evaluate karta hai aur agla sawal return karta hai.
    """
    client = get_groq_client()
    prompt = get_answer_evaluation_prompt(
        resume_text, jd_text, question, user_answer, question_number, total_questions
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            reasoning_format="hidden",
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise Exception(f"Answer evaluation me error aaya: {str(e)}")


def generate_final_report(resume_text: str, jd_text: str, qa_history: list) -> str:
    """
    Layer 5: Poore interview ke baad Final Markdown Report generate karta hai.
    """
    client = get_groq_client()
    prompt = get_final_report_prompt(resume_text, jd_text, qa_history)

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            reasoning_format="hidden"
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Final report generate karne me error aaya: {str(e)}")
