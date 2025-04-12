import whisper
from pydub import AudioSegment
import os
import uuid
import io

# Load Whisper model once
model = whisper.load_model("base")  # "tiny" or "small" may be faster for streaming

def transcribe_audio(audio_data: bytes, input_format: str = "wav") -> str:
    temp_filename = f"temp_{uuid.uuid4()}.{input_format}"
    with open(temp_filename, "wb") as f:
        f.write(audio_data)

    if input_format != "wav":
        audio = AudioSegment.from_file(temp_filename, format=input_format)
        wav_filename = temp_filename.replace(f".{input_format}", ".wav")
        audio.export(wav_filename, format="wav")
        os.remove(temp_filename)
        temp_filename = wav_filename

    result = model.transcribe(temp_filename)
    os.remove(temp_filename)
    return result["text"]

def transcribe_partial(audio_chunk: bytes) -> str:
    try:
        audio_io = io.BytesIO(audio_chunk)
        result = model.transcribe(audio_io, fp16=False, verbose=False)
        return result.get("text", "")
    except Exception as e:
        print(f"[transcribe_partial ERROR] {e}")
        return ""
