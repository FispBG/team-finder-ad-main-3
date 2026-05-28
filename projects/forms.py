# Сторонние библиотеки
from django import forms

# Локальные импорты
from .models import PROJECT_STATUS_CHOICES, Project
from .utils import validate_github


class ProjectForm(forms.ModelForm):
    """Форма для создания и редактирования проектов."""

    status = forms.ChoiceField(choices=PROJECT_STATUS_CHOICES, widget=forms.Select)

    class Meta:
        """Указываем модель и поля, которые будут отображаться в форме."""

        model = Project
        fields = ["name", "description", "github_url", "status"]

    def clean_github_url(self):
        """Проверяем, что ссылка на Github корректная."""
        return validate_github(self.cleaned_data.get("github_url"))
