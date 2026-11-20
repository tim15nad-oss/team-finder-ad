import random
from io import BytesIO
from uuid import uuid4

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from .constants import (
    AVATAR_FONT_SIZE,
    AVATAR_SIZE,
    AVATAR_TEXT_COLOR,
    AvatarBackground,
)


def make_avatar(letter: str) -> ContentFile:
    background = random.choice(list(AvatarBackground)).value
    image = Image.new('RGB', (AVATAR_SIZE, AVATAR_SIZE), background)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(str(settings.AVATAR_FONT_PATH), AVATAR_FONT_SIZE)
    left, top, right, bottom = draw.textbbox((0, 0), letter, font=font)
    x = (AVATAR_SIZE - (right - left)) / 2 - left
    y = (AVATAR_SIZE - (bottom - top)) / 2 - top
    draw.text((x, y), letter, fill=AVATAR_TEXT_COLOR, font=font)
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue(), name=f'{uuid4().hex}.png')
