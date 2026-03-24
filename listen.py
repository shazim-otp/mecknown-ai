import sounddevice as sd
import vosk
import json

# Load Vosk model
model = vosk.Model("vosk-model-small-en-us-0.15")
rec = vosk.KaldiRecognizer(model, 16000)

def listen():
    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=1
    ) as stream:
        while True:
            data, _ = stream.read(4000)

            # ✅ CFFI-safe conversion (FINAL FIX)
            if rec.AcceptWaveform(bytes(data)):
                result = json.loads(rec.Result())
                return result.get("text", "")

