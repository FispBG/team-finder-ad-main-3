# Сторонние библиотеки
from django import forms
from django.contrib.auth import get_user_model

# Локальные импорты
from .utils import validate_github, validate_phone_number

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    """Форма для регистрации нового пользователя."""

    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        """Указываем модель и поля, которые будут отображаться в форме."""

        model = User
        fields = ['name', 'surname', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Форма для входа пользователя."""

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())


class ProfileEditForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя.

    Позволяет изменять личные данные, телефон и ссылку на Github.
    """
    class Meta:
        """Указываем модель и поля, которые будут отображаться в форме."""

        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']

    def clean_phone(self):
        """Проверяем, что номер телефона соответствует формату и не занят другим пользователем."""
        phone = self.cleaned_data.get('phone')
        return validate_phone_number(phone, exclude_pk=self.instance.pk)

    def clean_github_url(self):
        """Проверяем, что ссылка на Github корректная."""
        return validate_github(self.cleaned_data.get('github_url'))


class PasswordChangeForm(forms.Form):
    """Форма для изменения пароля пользователя."""

    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password1 = forms.CharField(widget=forms.PasswordInput())
    new_password2 = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        """Проверяем, что текущий пароль указан верно."""
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Текущий пароль указан неверно.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password1')
        p2 = cleaned_data.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Новые пароли не совпадают.")
        return cleaned_data
