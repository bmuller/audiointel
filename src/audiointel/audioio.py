import asyncio
import logging
from collections import deque

import numpy as np
import sounddevice as sd

logger = logging.getLogger(__name__)


async def play_buffer(buff, channels, sample_rate):
    loop = asyncio.get_event_loop()
    event = asyncio.Event()
    idx = 0

    def callback(outdata, frame_count, time_info, status):
        nonlocal idx
        if status:
            logger.warning(status)
        remainder = len(buff) - idx
        if remainder == 0:
            loop.call_soon_threadsafe(event.set)
            raise sd.CallbackStop
        valid_frames = frame_count if remainder >= frame_count else remainder
        outdata[:valid_frames] = buff[idx : idx + valid_frames]
        outdata[valid_frames:] = 0
        idx += valid_frames

    with sd.OutputStream(
        callback=callback, dtype=buff.dtype, channels=channels, samplerate=sample_rate
    ):
        await event.wait()


async def audio_buffer_generator(maxsize, samplerate, channels):
    queue = deque([], maxsize)
    async for data, status in inputstream_generator(samplerate, channels):
        queue.append(data)
        yield np.concatenate(queue, axis=0, dtype=np.float32), status


async def inputstream_generator(samplerate, channels):
    q = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def callback(indata, frame_count, time_info, status):
        loop.call_soon_threadsafe(q.put_nowait, (indata.copy(), status))

    with sd.InputStream(
        samplerate=samplerate, channels=channels, callback=callback
    ) as stream:
        starttime = stream.time
        lastsec = 0
        buff = []
        while True:
            indata, status = await q.get()
            buff.append(indata)
            cursec = np.floor(stream.time - starttime)
            if cursec != lastsec:
                lastsec = cursec
                data = np.concatenate(buff, axis=0).flatten().astype(np.float32)
                buff.clear()
                yield data, status
