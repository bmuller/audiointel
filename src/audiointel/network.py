import hashlib
import logging
import os
import urllib

from tqdm import tqdm

logger = logging.getLogger(__name__)

# the following is taken in large part from:
# https://github.com/openai/whisper/blob/517a43ecd132a2089d85f4ebc044728a71d49f6e/whisper/__init__.py


def download(url, root, expected_sha256):
    os.makedirs(root, exist_ok=True)
    download_target = os.path.join(root, os.path.basename(url))

    if os.path.isfile(download_target):
        with open(download_target, "rb") as f:
            if hashlib.file_digest(f, "sha256").hexdigest() == expected_sha256:
                return download_target
            else:
                logger.warn(
                    "%s exists, but the SHA256 checksum does not match; re-downloading",
                    download_target,
                )

    logger.info("Attempting to download %s to %s", url, download_target)
    with urllib.request.urlopen(url) as source, open(download_target, "wb") as output:
        length = int(source.info().get("Content-Length"))
        with tqdm(
            total=length, ncols=80, unit="iB", unit_scale=True, unit_divisor=1024
        ) as loop:
            while True:
                buffer = source.read(8192)
                if not buffer:
                    break

                output.write(buffer)
                loop.update(len(buffer))

    with open(download_target, "rb") as f:
        if hashlib.file_digest(f, "sha256").hexdigest() != expected_sha256:
            msg = f"{download_target} downloaded but SHA256 checksum comparison failed"
            raise RuntimeError(msg)

    logger.debug("Download completed successfully")
    return download_target
