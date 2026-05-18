from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from common.constants import GITHUB_DOMAIN


class GitHubURLMixin:
    """Миксин для валидации GitHub URL."""

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            try:
                URLValidator()(url)
            except ValidationError:
                raise ValidationError('Введите корректный URL')
            if GITHUB_DOMAIN not in url:
                raise ValidationError('Ссылка должна вести на GitHub')
        return url
