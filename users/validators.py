from urllib.parse import urlparse

from django.core.exceptions import ValidationError

GITHUB_HOSTS = ('github.com', 'www.github.com')


def validate_github_url(value: str) -> None:
    if not value:
        return
    host = (urlparse(value).hostname or '').lower()
    if host not in GITHUB_HOSTS:
        raise ValidationError('Ссылка должна вести на GitHub.')
