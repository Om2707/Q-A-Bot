import speech_recognition as sr
from typing import Optional

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


def transcribe_audio(audio_file, use_whisper: bool = False, openai_api_key: Optional[str] = None) -> str:
    """
    Transcribe an audio file (file-like object or file path) to text.
    If use_whisper is True and OpenAI is available, use Whisper API.
    Otherwise, use SpeechRecognition's default recognizer (Google Web Speech API).
    """
    recognizer = sr.Recognizer()
    try:
        if isinstance(audio_file, str):
            audio_source = sr.AudioFile(audio_file)
        else:
            audio_source = sr.AudioFile(audio_file)
        with audio_source as source:
            audio = recognizer.record(source)
        if use_whisper and HAS_OPENAI and openai_api_key:
            # Use OpenAI Whisper API
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as tmp:
                tmp.write(audio.get_wav_data())
                tmp.flush()
                openai.api_key = openai_api_key
                with open(tmp.name, 'rb') as f:
                    transcript = openai.Audio.transcribe('whisper-1', f)
                return transcript['text']
        else:
            # Use Google Web Speech API (free, but requires internet)
            return recognizer.recognize_google(audio)
    except Exception as e:
        return f"[Voice transcription error: {str(e)}]" 