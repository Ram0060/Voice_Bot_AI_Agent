from gtts import gTTS
import uuid
import os

def text_to_speech(text: str, output_dir="audio_responses") -> str:
    if not text.strip():
        raise ValueError("Text for TTS is empty.")

    os.makedirs(output_dir, exist_ok=True)

    filename = f"reply_{uuid.uuid4()}.mp3"
    filepath = os.path.abspath(os.path.join(output_dir, filename))

    print(f"🔊 Generating speech for: {text}")
    print(f"📁 Saving audio to: {filepath}")

    try:
        tts = gTTS(text=text, lang="en")
        tts.save(filepath)
        print("✅ Text-to-speech audio saved successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to generate TTS audio: {e}")
        raise e

    return filepath
