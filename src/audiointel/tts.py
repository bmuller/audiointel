import logging
import os

import numpy as np
from kokoro_onnx import Kokoro
from nltk.tokenize import sent_tokenize

from .audioio import play_buffer
from .network import download

logger = logging.getLogger(__name__)

MODEL_FILE_SOURCE = (
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
    "7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5",
)
VOICES_FILE_SOURCE = (
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
    "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d",
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
        if len(msg) > 50:
            for sentence in sent_tokenize(msg):
                await self._say(sentence.strip())
        else:
            await self._say(msg.strip())

    async def _say(self, msg):
        samples, sample_rate = self.model.create(
            msg, voice=self.voice, speed=self.speed, lang=self.lang
        )
        shaped_samples = np.reshape(samples, (np.size(samples), self.channels))
        await play_buffer(shaped_samples, self.channels, sample_rate)
