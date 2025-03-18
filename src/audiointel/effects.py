import soundfile as sf

from .audioio import play_buffer
from .utils import get_datafile_path


class Sounds:
    WAKEUP = get_datafile_path("wake.mp3")
    THINKING = get_datafile_path("thinking.mp3")
    ERROR = get_datafile_path("error.mp3")


LOADED = {}


async def play_sound(sound):
    if sound not in LOADED:
        LOADED[sound] = sf.read(sound, dtype="float32")
    data, sample_rate = LOADED[sound]
    await play_buffer(data, 2, sample_rate)
