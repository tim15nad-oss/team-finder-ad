import random
from io import BytesIO
from uuid import uuid4

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

BACKGROUNDS = ('#dce7f5', '#f5e6dc', '#e1f2e3', '#f3dcec', '#f7f0cf')
TEXT_COLOR = '#333a4a'
SIZE = 256
FONT_SIZE = 128


def make_avatar(letter: str) -> ContentFile:
    image = Image.new('RGB', (SIZE, SIZE), random.choice(BACKGROUNDS))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(str(settings.AVATAR_FONT_PATH), FONT_SIZE)
    left, top, right, bottom = draw.textbbox((0, 0), letter, font=font)
    x = (SIZE - (right - left)) / 2 - left
    y = (SIZE - (bottom - top)) / 2 - top
    draw.text((x, y), letter, fill=TEXT_COLOR, font=font)
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue(), name=f'{uuid4().hex}.png')
