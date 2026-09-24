from urllib.parse import urlparse

from django.core.exceptions import ValidationError


def validate_github_url(value):
    """Ссылка должна вести именно на GitHub."""
    if not value:
        return
    host = (urlparse(value).hostname or '').lower()
    if host not in ('github.com', 'www.github.com'):
        raise ValidationError('Ссылка должна вести на GitHub (github.com)')