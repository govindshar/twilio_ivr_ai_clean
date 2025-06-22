from flask import Flask, request, send_file
from twilio.twiml.voice_response import VoiceResponse
import os
import uuid
import requests
import time
import json
from whisper_stt import transcribe
from chatbot import ask_ai
from tts import generate_audio
from pydub import AudioSegment

# === Setup ===
AudioSegment.converter = "ffmpeg"  # Use default in Render (Linux environment)

account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "dummy_sid")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "dummy_token")

app = Flask(__name__)
os.makedirs("recordings", exist_ok=True)
os.makedirs("responses", exist_ok=True)
os.makedirs("history", exist_ok=True)

processing_status = {}  # { callSid: {status, session_id} }

# === Handle Incoming Call ===
@app.route("/voice", methods=["POST"])
def handle_call():
    print("📞 Incoming call received")
    response = VoiceResponse()
    response.say("Please record your question after the beep. Press any key when done.", voice='alice')
    response.record(timeout=5, transcribe=False, maxLength=10, action="/process_twilio_audio")
    return str(response)

# === Process the Recording ===
@app.route("/process_twilio_audio", methods=["POST"])
def process_twilio_audio():
    recording_url = request.form.get("RecordingUrl")
    call_sid = request.form.get("CallSid") or str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    print("🎙️ Received recording from:", recording_url)
    print("➡️ Call SID:", call_sid)
    print("➡️ Session ID:", session_id)

    if not recording_url:
        print("❌ No recording URL received.")
        return "Missing RecordingUrl", 400

    mp3_url = recording_url + ".mp3"
    mp3_path = f"recordings/{session_id}.mp3"
    wav_path = f"recordings/{session_id}.wav"
    output_audio = f"responses/{session_id}.wav"

    response = VoiceResponse()
    response.say("Please wait while I generate your answer.", voice='alice')
    response.redirect(f"/play_ready_audio?callSid={call_sid}")

    # Background task
    def process_audio():
        print("⚙️ Starting audio processing thread...")
        try:
            for attempt in range(3):
                r = requests.get(mp3_url, auth=(account_sid, auth_token))
                if r.status_code == 200:
                    with open(mp3_path, "wb") as f:
                        f.write(r.content)
                    break
                time.sleep(2)
            else:
                raise Exception("Download failed after 3 attempts")

            audio = AudioSegment.from_mp3(mp3_path)
            audio.export(wav_path, format="wav")

            user_input = ""
            for _ in range(3):
                user_input = transcribe(wav_path).strip()
                if user_input:
                    break
                time.sleep(2)

            print("🧠 Transcribed:", user_input)

            if not user_input:
                fallback = "Sorry, I could not hear you clearly. Please try again."
                generate_audio(fallback, output_audio)
                processing_status[call_sid] = {"status": "ready", "session_id": session_id}
                return

            history_path = f"history/{call_sid}.json"
            chat_history = []
            if os.path.exists(history_path):
                with open(history_path, "r", encoding="utf-8") as f:
                    chat_history = json.load(f)

            chat_history.append({"role": "user", "content": user_input})
            reply = ask_ai(chat_history)

            if len(reply) > 400:
                reply = reply[:400].rsplit(".", 1)[0] + "."

            chat_history.append({"role": "assistant", "content": reply})
            with open(history_path, "w", encoding="utf-8") as f:
                json.dump(chat_history, f, indent=2)

            print("🗣️ TTS reply:", reply)
            generate_audio(reply, output_audio)

            processing_status[call_sid] = {"status": "ready", "session_id": session_id}
            print(f"✅ Audio ready for session {session_id}")

        except Exception as e:
            print("❌ Processing error:", e)
            processing_status[call_sid] = {"status": "error"}

    import threading
    threading.Thread(target=process_audio).start()

    return str(response)

# === Poll & Play Audio Once Ready ===
@app.route("/play_ready_audio", methods=["GET", "POST"])
def play_ready_audio():
    call_sid = request.values.get("callSid")
    response = VoiceResponse()

    print("🔁 Polling audio readiness for:", call_sid)

    for _ in range(40):
        status_info = processing_status.get(call_sid)
        if status_info:
            break
        time.sleep(1)

    if status_info and status_info["status"] == "ready":
        session_id = status_info["session_id"]
        print(f"✅ Found ready audio: {session_id}")
        audio_url = f"{request.url_root}play_response/{session_id}?ts={int(time.time())}"
        response.play(url=audio_url)
        processing_status.pop(call_sid, None)
        response.redirect("/voice")
    else:
        print("❌ Timeout or error: No audio ready.")
        response.say("Sorry, the response took too long or failed. Please try again.", voice='alice')
        response.hangup()

    return str(response)

# === Serve Audio File ===
@app.route("/play_response/<audio_id>")
def play_response(audio_id):
    path = f"responses/{audio_id}.wav"
    print(f"🎧 Serving audio file: {path}")
    if not os.path.exists(path):
        return "Audio not found", 404
    return send_file(path, mimetype="audio/wav")

# === Run App on Render ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
