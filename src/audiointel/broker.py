import logging

from .effects import Sounds, play_sound
from .llm import LLMHelper
from .stt import Listener
from .tts import Speaker

logger = logging.getLogger(__name__)


class Broker:
    def __init__(self, wake_word="robot"):
        self.wake_word = wake_word
        self.speaker = Speaker()
        self.listener = Listener()
        self.llm = LLMHelper()

    async def say(self, msg):
        logger.debug("Saying: %s", msg)
        return await self.speaker.say(msg)

    async def wait_for_word(self, word):
        logger.debug("Waiting for word: %s", word)
        await self.listener.wait_for(word)
        logger.debug("Wake word heard: %s", word)

    async def record_input(self, maxtime=30, pause=2):
        # TODO - be more intelligent - wait for speaker to finish statement/question
        logger.debug("Recording input")
        sounds = await self.listener.record_input(maxtime, pause)
        logger.debug("Finished recording input")
        text = self.listener.transcribe(sounds)
        logger.info("Recorded and transcribed: %s", text)
        return text

    async def confirm(self, question, max_attempts=None):
        attempts = 1
        text = await self.ask(question)
        result = await self.llm.to_boolean(text)
        while result is None and (max_attempts is None or attempts <= max_attempts):
            await play_sound(Sounds.ERROR)
            await self.say("Please respond with a yes or no.")
            attempts += 1
            text = await self.ask(question)
            result = await self.llm.to_boolean(text)
        return result

    async def ask(self, question):
        await self.say(question)
        await play_sound(Sounds.WAKEUP)
        text = await self.record_input()
        await play_sound(Sounds.THINKING)
        return text

    async def wake_listen_loop(self, maxtime=30, pause=2):
        await self.wait_for_word(self.wake_word)
        await play_sound(Sounds.WAKEUP)
        text = await self.record_input(maxtime, pause)
        await play_sound(Sounds.THINKING)
        yield text
