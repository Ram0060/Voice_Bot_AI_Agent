import os
import uuid
import openai

def text_to_speech(text: str, output_dir="audio_responses") -> str:
    if not text.strip():
        raise ValueError("Text for TTS is empty.")

    os.makedirs(output_dir, exist_ok=True)
    filename = f"reply_{uuid.uuid4()}.mp3"
    filepath = os.path.abspath(os.path.join(output_dir, filename))

    print(f"🎙️ Generating TTS for: {text}")
    response = openai.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
    response.stream_to_file(filepath)

    print(f"✅ Saved OpenAI TTS: {filepath}")
    return filepath
