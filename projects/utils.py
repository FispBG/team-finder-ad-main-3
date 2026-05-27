# Стандартные библиотеки
from urllib.parse import urlparse

# Сторонние библиотеки
from django import forms


def validate_github(url):
    """Проверка, что предоставленная ссылка ведет на Github."""
    if url:
        parsed = urlparse(url)
        if 'github.com' not in parsed.netloc.lower():
            raise forms.ValidationError("Ссылка должна вести именно на Github.")
    return url
