import whisper
import os

# ✅ Add correct ffmpeg path
os.environ["PATH"] += os.pathsep + r"C:\Users\Govind\Downloads\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin"

# Load Whisper model once
model = whisper.load_model("base")

def transcribe(audio_path):
    """
    Transcribes the given audio file using OpenAI's Whisper model.

    Args:
        audio_path (str): Path to the audio file to transcribe.

    Returns:
        str: The transcribed text.
    """
    result = model.transcribe(audio_path)
    return result["text"]
