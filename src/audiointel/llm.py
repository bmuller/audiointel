import logging

from langchain_ollama import OllamaLLM

logger = logging.getLogger(__name__)

BOOL_PROMPT = """
Does the following Input indicate indicate agreement or affirmation?

Respond with Yes or No.

Input: {input}
"""


class LLMHelper:
    def __init__(self, model="mistral"):
        self.model = OllamaLLM(model="mistral", temperature=0)

    async def to_boolean(self, text):
        logger.debug("Attempting to coerce the following to boolean: %s", text)
        result = await self.model.ainvoke(BOOL_PROMPT.format(input=text))
        fresult = result.strip()
        if fresult not in ["Yes", "No"]:
            logger.debug("Could not turn input into boolean: %s", fresult)
            return None
        logger.debug("Input is treated as: %s", fresult == "Yes")
        return fresult == "Yes"
