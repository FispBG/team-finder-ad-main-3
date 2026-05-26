from django import forms
from .models import Project
from urllib.parse import urlparse


def validate_github(url):
    """Проверка, что предоставленная ссылка ведет на Github."""
    if url:
        parsed = urlparse(url)
        if 'github.com' not in parsed.netloc.lower():
            raise forms.ValidationError("Ссылка должна вести именно на Github.")
    return url


class ProjectForm(forms.ModelForm):
    """Форма для создания и редактирования проектов."""

    status = forms.ChoiceField(choices=Project.STATUS_CHOICES, widget=forms.Select)

    class Meta:
        """Указываем модель и поля, которые будут отображаться в форме."""

        model = Project
        fields = ['name', 'description', 'github_url', 'status']

    def clean_github_url(self):
        """Проверяем, что ссылка на Github корректная."""
        return validate_github(self.cleaned_data.get('github_url'))
