import pvporcupine
import sounddevice as sd
import numpy as np

ACCESS_KEY = "3hZcGS3UavCu7XiAV+5iSV0j0aehGS9GJFIMJQOnaQV6Rii9/ISd0Q=="

WAKE_WORDS = ["jarvis", "computer"]

class WakeWord:
    def __init__(self):
        self.porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keywords=WAKE_WORDS
        )

    def listen(self):
        with sd.RawInputStream(
            samplerate=self.porcupine.sample_rate,
            blocksize=self.porcupine.frame_length,
            dtype="int16",
            channels=1
        ) as stream:
            while True:
                pcm_bytes, _ = stream.read(self.porcupine.frame_length)
                pcm = np.frombuffer(pcm_bytes, dtype=np.int16).tolist()

                if self.porcupine.process(pcm) >= 0:
                    return
