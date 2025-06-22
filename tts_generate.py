# tts_generate.py
from TTS.api import TTS

# Load model once
model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)

def generate_tts(text, output_path):
    model.tts_to_file(text=text, file_path=output_path)
    return output_path
