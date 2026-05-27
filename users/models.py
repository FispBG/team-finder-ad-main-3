# Сторонние библиотеки
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

# Локальные импорты
from .managers import UserManager
from .utils import generate_default_avatar

SKILL_NAME_MAX_LENGTH = 100
USER_NAME_MAX_LENGTH = 124
USER_PHONE_MAX_LENGTH = 12
USER_ABOUT_MAX_LENGTH = 256


class Skill(models.Model):
    """Модель для хранения навыков пользователей."""

    name = models.CharField(max_length=SKILL_NAME_MAX_LENGTH, unique=True)

    class Meta:
        """Устанавливаем порядок сортировки навыков по имени."""

        ordering = ['name']

    def __str__(self):
        return str(self.name)


class User(AbstractBaseUser, PermissionsMixin):
    """Модель для представления пользователя в системе."""

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    phone = models.CharField(max_length=USER_PHONE_MAX_LENGTH, unique=True, blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    about = models.TextField(max_length=USER_ABOUT_MAX_LENGTH, blank=True, null=True)

    skills = models.ManyToManyField(Skill, blank=True, related_name='users')
    favorites = models.ManyToManyField('projects.Project',
                                       blank=True, related_name='interested_users')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    def save(self, *args, **kwargs):
        """Переопределяем метод сохранения."""
        if not self.avatar and self.name:
            filename, content_file = generate_default_avatar(self.name)
            if filename and content_file:
                self.avatar.save(filename, content_file, save=False)

        if self.phone and self.phone.startswith("8"):
            self.phone = "+7" + self.phone[1:]

        super().save(*args, **kwargs)
