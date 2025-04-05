import whisper
from pydub import AudioSegment
import os
import uuid

model = whisper.load_model("base")  # You can use "small" or "medium" if needed

def transcribe_audio(audio_data: bytes, input_format: str = "wav") -> str:
    # Generate a unique filename
    temp_filename = f"temp_{uuid.uuid4()}.{input_format}"

    # Save raw audio data to file
    with open(temp_filename, "wb") as f:
        f.write(audio_data)

    # Convert to wav if needed (Twilio might send audio in mp3, etc.)
    if input_format != "wav":
        audio = AudioSegment.from_file(temp_filename, format=input_format)
        wav_filename = temp_filename.replace(f".{input_format}", ".wav")
        audio.export(wav_filename, format="wav")
        os.remove(temp_filename)
        temp_filename = wav_filename

    # Transcribe using Whisper
    result = model.transcribe(temp_filename)
    
    # Clean up
    os.remove(temp_filename)

    return result["text"]
