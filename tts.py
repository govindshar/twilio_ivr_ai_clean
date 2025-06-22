from TTS.api import TTS
import os

# ✅ Initialize TTS model once (Tacotron2-DDC + HiFi-GAN)
try:
    print("[TTS] Loading model: Tacotron2-DDC")
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)
except Exception as e:
    print("❌ Failed to load TTS model:", e)
    tts = None

def generate_audio(text: str, output_path: str):
    """
    Generate speech audio from text and save as a WAV file.

    Args:
        text (str): The text to convert into speech.
        output_path (str): Path to save the output .wav file.
    """
    if tts is None:
        print("❌ Cannot generate audio: TTS model not loaded.")
        return

    try:
        print(f"[TTS] Generating audio for: '{text}'")
        tts.tts_to_file(text=text, file_path=output_path)
        print(f"[TTS] ✅ Audio saved to: {output_path}")
    except Exception as e:
        print("❌ TTS generation failed:", e)
