from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image  # type: ignore


def get_default_art_cover() -> bytes:
    p = Path(__file__).parent.resolve() / "assets/default.png"
    return p.read_bytes()


def playtime_to_str(value: int | float):
    """Returns string in `M:S` format from playtime in seconds"""
    m, s = divmod(round(value), 60)
    return f"{m}:{s:02}"


def resize_img(image: BytesIO) -> bytes:
    """Resizes song cover art to fit into `Metadata` frame.

    Args:
        `image`: Cover art from audio file metadata.

    Returns:
        Resized image
    """
    img = Image.open(image)
    width, height = img.size
    scale = min(256 / height, 256 / width)
    img = img.resize((int(width * scale), int(height * scale)), Image.ANTIALIAS)
    b_img = BytesIO()
    img.save(b_img, format="PNG")

    return b_img.getvalue()
