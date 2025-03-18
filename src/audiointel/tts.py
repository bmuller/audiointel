import logging
import os

import numpy as np
from kokoro_onnx import Kokoro

from .audioio import play_buffer
from .network import download

logger = logging.getLogger(__name__)

MODEL_FILE_SOURCE = (
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
    "7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5",
)
VOICES_FILE_SOURCE = (
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
    "d19762d46cf0e6648cb28a7711df1637aad15818185d13f4ff840d57f2f6dfed",
)


class Speaker:
    def __init__(self, channels=1, voice="bf_emma", speed=0.9, lang="en-gb"):
        cachedir = os.path.join(os.path.expanduser("~"), ".cache", "kokoro")
        model_path = download(MODEL_FILE_SOURCE[0], cachedir, MODEL_FILE_SOURCE[1])
        voices_path = download(VOICES_FILE_SOURCE[0], cachedir, VOICES_FILE_SOURCE[1])
        self.model = Kokoro(model_path, voices_path)
        self.channels = channels
        self.voice = voice
        self.speed = speed
        self.lang = lang

    async def say(self, msg):
        samples, sample_rate = self.model.create(
            msg, voice=self.voice, speed=self.speed, lang=self.lang
        )
        shaped_samples = np.reshape(samples, (np.size(samples), self.channels))
        await play_buffer(shaped_samples, self.channels, sample_rate)
