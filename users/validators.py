from urllib.parse import urlparse

from django.core.exceptions import ValidationError

from .constants import GITHUB_HOSTS


def validate_github_url(value: str) -> None:
    if not value:
        return
    host = (urlparse(value).hostname or '').lower()
    if host not in GITHUB_HOSTS:
        raise ValidationError('Ссылка должна вести на GitHub.')
