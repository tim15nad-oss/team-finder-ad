import random
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

AVATAR_SIZE = 256
BACKGROUNDS = ['#DCE7F5', '#E4F1E4', '#F5E6DC', '#EDE4F5', '#F5F0D6', '#DDEFF0']
LETTER_COLOR = '#333A4A'


def _load_font(size):
    try:
        return ImageFont.truetype(str(settings.AVATAR_FONT_PATH), size)   # .otf из static/fonts
    except OSError:
        return ImageFont.load_default()      # запасной вариант: кириллица может не отрисоваться


def make_avatar_file(name: str) -> ContentFile:
    """PNG с первой буквой имени на случайном однотонном фоне."""
    letter = (name.strip()[:1] or '?').upper()
    image = Image.new('RGB', (AVATAR_SIZE, AVATAR_SIZE), random.choice(BACKGROUNDS))
    draw = ImageDraw.Draw(image)
    font = _load_font(int(AVATAR_SIZE * 0.5))

    left, top, right, bottom = draw.textbbox((0, 0), letter, font=font)
    x = (AVATAR_SIZE - (right - left)) / 2 - left
    y = (AVATAR_SIZE - (bottom - top)) / 2 - top
    draw.text((x, y), letter, fill=LETTER_COLOR, font=font)

    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue())