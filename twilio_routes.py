from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse
from app.stt import transcribe_audio
from app.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, GCP_BUCKET_NAME
from app.assistant import get_assistant_response
from app.tts import text_to_speech
from app.gcs import upload_file_to_gcs

from pydub import AudioSegment
import requests
import uuid
import os
import time

router = APIRouter()

# STEP 1: Greet the caller and ask them to leave a message
@router.post("/voice")
async def voice_webhook():
    response = VoiceResponse()
    response.say("Hi! Please leave your message after the beep. Press any key when you're done.", voice="alice")
    response.record(
        action="/twilio/recording",
        method="POST",
        max_length=60,
        timeout=5,
        finish_on_key="#",
        recording_status_callback="/twilio/recording-status"
    )
    response.say("Thanks! Goodbye.")
    return PlainTextResponse(str(response), media_type="application/xml")


# STEP 2: Log when recording is marked complete by Twilio
@router.post("/recording-status")
async def recording_status_webhook(request: Request):
    form = await request.form()
    print(f"🎯 Twilio says recording is completed — duration: {form.get('RecordingDuration')} sec")
    print(f"🎯 ✅ Recording is ready: {form.get('RecordingUrl')}")
    return PlainTextResponse("OK")


# STEP 3: Handle voice recording webhook and start transcription
@router.post("/recording")
async def recording_webhook(request: Request, background_tasks: BackgroundTasks):
    form = await request.form()
    recording_url = form.get("RecordingUrl")

    print(f"[Twilio] Received recording URL: {recording_url}")
    background_tasks.add_task(handle_transcription, recording_url)

    response = VoiceResponse()
    response.say("Thanks for your message. We'll get back to you shortly.", voice="alice")
    return PlainTextResponse(str(response), media_type="application/xml")


# STEP 4: Download, re-encode, transcribe with Whisper, and call Assistant
def handle_transcription(recording_url: str):
    try:
        raw_path = f"raw_{uuid.uuid4()}"
        clean_path = f"clean_{uuid.uuid4()}.wav"

        print("⏳ Waiting for recording to be fully available...")
        time.sleep(5)

        # Download audio
        response = requests.get(recording_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
        content_type = response.headers.get("Content-Type", "")
        print(f"[DEBUG] Content-Type from Twilio: {content_type}")

        if "audio" not in content_type:
            raise ValueError(f"Invalid response from Twilio — Content-Type: {content_type}")

        ext = content_type.split("/")[-1]
        raw_path += f".{ext}"
        with open(raw_path, "wb") as f:
            f.write(response.content)

        audio = AudioSegment.from_file(raw_path)
        print(f"🎧 Clean audio duration: {audio.duration_seconds:.2f} seconds")

        audio.export(clean_path, format="wav")
        os.remove(raw_path)

        with open(clean_path, "rb") as f:
            audio_bytes = f.read()

        transcription = transcribe_audio(audio_bytes, input_format="wav")
        print("\n📜 Transcription:")
        print(transcription)
        print("📜 End of Transcription\n")

        assistant_reply = get_assistant_response(transcription)
        print("🤖 Assistant Response:")
        print(assistant_reply)

        # Convert to speech
        tts_path = text_to_speech(assistant_reply)

        # Upload to GCS with debug
        print("📦 Attempting to upload to GCS...")
        print("🔍 File exists:", os.path.exists(tts_path))
        print("📍 TTS path:", tts_path)
        print("🪣 Bucket name:", GCP_BUCKET_NAME)

        try:
            public_url = upload_file_to_gcs(tts_path)
            print(f"✅ File uploaded successfully! Public URL: {public_url}")
        except Exception as upload_error:
            print(f"[GCS ERROR] Upload failed: {upload_error}")

        # Clean up
        os.remove(clean_path)
        os.remove(tts_path)

    except Exception as e:
        print(f"[ERROR] Transcription pipeline failed: {e}")
