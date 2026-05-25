from django import forms
from django.contrib.auth import get_user_model
from urllib.parse import urlparse
import re
from .models import Project

User = get_user_model()


def validate_github(url):
    if url:
        parsed = urlparse(url)
        if 'github.com' not in parsed.netloc.lower():
            raise forms.ValidationError("Ссылка должна вести именно на Github.")
    return url


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            return phone

        if phone.startswith('8'):
            normalized = '+7' + phone[1:]
        else:
            normalized = phone

        if not re.match(r'^\+7\d{10}$|^8\d{10}$', phone):
            raise forms.ValidationError("Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX.")

        qs = User.objects.filter(phone=normalized).exclude(pk=self.instance.pk)
        if phone.startswith('+7'):
            qs = qs | User.objects.filter(phone='8' + phone[2:]).exclude(pk=self.instance.pk)
        elif phone.startswith('8'):
            qs = qs | User.objects.filter(phone='+7' + phone[1:]).exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("Пользователь с таким номером телефона уже существует.")
        return phone

    def clean_github_url(self):
        return validate_github(self.cleaned_data.get('github_url'))


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password1 = forms.CharField(widget=forms.PasswordInput())
    new_password2 = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
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


class ProjectForm(forms.ModelForm):
    status = forms.ChoiceField(choices=Project.STATUS_CHOICES, widget=forms.Select)

    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']

    def clean_github_url(self):
        return validate_github(self.cleaned_data.get('github_url'))
