import logging

import numpy as np
import whisper

from .audioio import audio_buffer_generator

# TODO https://github.com/SYSTRAN/faster-whisper

logger = logging.getLogger(__name__)


class Listener:
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.model = whisper.load_model("tiny.en")

    def is_silence(self, buff):
        return np.max(np.abs(buff)) <= 0.01

    def transcribe(self, buff):
        if not self.is_silence(buff):
            result = self.model.transcribe(buff, language="en")
            if len([s for s in result["segments"] if s["no_speech_prob"] < 0.3]) > 0:
                text = result["text"].strip()
                return text if text != "" else None
        return None

    async def wait_for(self, word):
        loop = audio_buffer_generator(2, self.sample_rate, self.channels)
        async for buff, _status in loop:
            text = self.transcribe(buff)
            # TODO - use a sentence tokenizer here
            if text and word.lower() in text.lower():
                return

    async def record_input(self, maxtime=30, pause=2):
        loop = audio_buffer_generator(maxtime, self.sample_rate, self.channels)
        async for buff, _status in loop:
            seconds = np.ceil(len(buff) / float(self.sample_rate))

            # if we reached our max time, return what we have
            if seconds > maxtime:
                return buff

            secs_silence = 0
            for second in np.array_split(np.flip(buff), seconds):
                if self.is_silence(second):
                    secs_silence += 1

                if secs_silence == pause:
                    return buff
