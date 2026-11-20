import re
from enum import Enum

NAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
PHONE_INPUT_MAX_LENGTH = 32
ABOUT_MAX_LENGTH = 256

PHONE_PATTERN = re.compile(r'(8|\+7)\d{10}')
PHONE_SEPARATORS = re.compile(r'[\s()\-]')
PHONE_LOCAL_PREFIX = '8'
PHONE_INTERNATIONAL_PREFIX = '+7'

GITHUB_HOSTS = ('github.com', 'www.github.com')

AVATAR_SIZE = 256
AVATAR_FONT_SIZE = 128
AVATAR_TEXT_COLOR = '#333a4a'


class AvatarBackground(str, Enum):

    LIGHT_BLUE = '#dce7f5'
    PEACH = '#f5e6dc'
    MINT = '#e1f2e3'
    PINK = '#f3dcec'
    CREAM = '#f7f0cf'
