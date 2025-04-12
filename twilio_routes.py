from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from twilio.twiml.voice_response import VoiceResponse, Connect
from twilio.rest import Client

from app.stt import transcribe_partial
from app.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, BASE_WEBHOOK_URL
from app.assistant import get_assistant_response
from app.tts import text_to_speech
from app.gcs import upload_file_to_gcs

import os
import uuid
import openai
import json
import base64
import wave

router = APIRouter()
AUDIO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio_responses"))
conversation_history = {}

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@router.post("/voice")
async def voice_webhook(request: Request):
    form = await request.form()
    call_sid = form.get("CallSid")

    if call_sid not in conversation_history:
        thread = openai.beta.threads.create()
        conversation_history[call_sid] = {
            "thread_id": thread.id,
            "turns": [],
            "audio_input_chunks": bytearray()
        }

    stream_url = f"{request.base_url}twilio/stream"
    response = VoiceResponse()
    connect = Connect()
    connect.stream(url=stream_url)
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")

@router.websocket("/twilio/stream")
async def twilio_stream(websocket: WebSocket):
    await websocket.accept()
    call_sid = str(uuid.uuid4())
    thread_id = None

    try:
        async for message in websocket.iter_text():
            data = json.loads(message)

            if data.get("event") == "start":
                call_sid = data["streamSid"]
                if call_sid not in conversation_history:
                    thread = openai.beta.threads.create()
                    conversation_history[call_sid] = {
                        "thread_id": thread.id,
                        "turns": [],
                        "audio_input_chunks": bytearray()
                    }
                thread_id = conversation_history[call_sid]["thread_id"]

            elif data.get("event") == "media":
                audio_payload = data["media"]["payload"]
                audio_bytes = base64.b64decode(audio_payload)
                conversation_history[call_sid]["audio_input_chunks"].extend(audio_bytes)

            elif data.get("event") == "stop":
                audio_bytes = conversation_history[call_sid]["audio_input_chunks"]
                transcription = transcribe_partial(audio_bytes)
                print(f"📝 Transcription: {transcription}")

                if transcription.lower().strip() in ["bye", "goodbye", "exit"]:
                    finalize_and_upload(call_sid)
                    await websocket.close()
                    return

                reply = get_assistant_response(transcription, thread_id)
                print(f"🤖 Assistant: {reply}")

                tts_path = text_to_speech(reply)
                filename = os.path.basename(tts_path)

                conversation_history[call_sid]["turns"].append({
                    "user": transcription,
                    "assistant": reply
                })

                conversation_history[call_sid]["audio_input_chunks"] = bytearray()

                # ✅ Redirect Twilio to play audio via BASE_WEBHOOK_URL
                client.calls(call_sid).update(
                    url=f"{BASE_WEBHOOK_URL}/twilio/play_audio?filename={filename}",
                    method="POST"
                )

                await websocket.close()
                return

    except WebSocketDisconnect:
        print("⚠️ WebSocket disconnected.")
    except Exception as e:
        print(f"[ERROR] WebSocket stream failed: {e}")

@router.post("/play_audio")
async def play_audio(request: Request):
    form = await request.form()
    filename = form.get("filename") or request.query_params.get("filename")

    response = VoiceResponse()
    response.play(f"{request.base_url}twilio/static-audio/{filename}")
    response.redirect(f"{request.base_url}twilio/voice")
    return HTMLResponse(str(response), media_type="application/xml")

@router.get("/static-audio/{filename}")
async def static_audio(filename: str):
    filepath = os.path.join(AUDIO_DIR, filename)
    return FileResponse(path=filepath, media_type="audio/mpeg")

def finalize_and_upload(call_sid: str):
    history = conversation_history.get(call_sid)
    if not history:
        return

    try:
        wav_path = os.path.join(AUDIO_DIR, f"{call_sid}_raw_input.wav")
        with wave.open(wav_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(8000)
            wf.writeframes(history["audio_input_chunks"])
        upload_file_to_gcs(wav_path)
        os.remove(wav_path)

        txt_path = os.path.join(AUDIO_DIR, f"{call_sid}_transcript.txt")
        with open(txt_path, "w") as f:
            for turn in history["turns"]:
                f.write(f"User: {turn['user']}\nAssistant: {turn['assistant']}\n\n")
        upload_file_to_gcs(txt_path)
        os.remove(txt_path)

    except Exception as e:
        print(f"[Finalize ERROR]: {e}")

    del conversation_history[call_sid]
