import io
from gtts import gTTS
from src.interview_engine import get_groq_client

def text_to_speech(text: str) -> bytes:
    """
    AI Interviewer ka sawal ko natural audio (MP3 bytes) me badalta hai.
    """

    tts = gTTS(text=text, lang="en", tld="co.in", slow=False)
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.read()

def speech_to_text(audio_bytes) -> str:
    """
    Candidate ki recorded voice ko Groq Whisper API se text me convrt karta hai.
    """

    client = get_groq_client()
    try:
        transcription = client.chat.completions.create(
            file=("answer.way", audio_bytes),
            model="whisper-large-v3-turbo",
            response_format="text"
        )
        return transcription.strip()
    except Exception as e:
        raise Exception(f"Voice transcribe karne me error aaya: {str(e)}")