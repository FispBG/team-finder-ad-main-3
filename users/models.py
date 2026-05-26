import io
import random
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


class UserManager(BaseUserManager):
    """Менеджер для модели User, обеспечивающий создание пользователей и суперпользователей."""

    def create_user(self, email, name, surname, password=None, **extra_fields):
        """Создает и сохраняет пользователя с указанными данными."""
        if not email:
            raise ValueError('Email является обязательным полем')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        """Создает и сохраняет суперпользователя с указанными данными."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, surname, password, **extra_fields)


class Skill(models.Model):
    """Модель для хранения навыков пользователей."""

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        """Устанавливаем порядок сортировки навыков по имени."""

        ordering = ['name']


class User(AbstractBaseUser, PermissionsMixin):
    """Модель для представления пользователя в системе."""

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    phone = models.CharField(max_length=12, unique=True, blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    about = models.TextField(max_length=256, blank=True, null=True)

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
            first_letter = self.name[0].upper()
            bg_colors = [
                (41, 128, 185), (39, 174, 96), (142, 68, 173),
                (230, 126, 34), (192, 57, 43), (44, 62, 80)
            ]
            bg_color = random.choice(bg_colors)

            img = Image.new('RGB', (200, 200), color=bg_color)
            draw = ImageDraw.Draw(img)

            try:
                font = ImageFont.truetype("Arial.ttf", 100)
            except IOError:
                font = ImageFont.load_default()

            if hasattr(draw, 'textsize'):
                text_width, text_height = draw.textsize(first_letter, font=font)
            elif hasattr(draw, 'textbbox'):
                bbox = draw.textbbox((0, 0), first_letter, font=font)
                text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            else:
                text_width, text_height = (70, 100)

            position = ((200 - text_width) / 2, (200 - text_height) / 2 - 10)
            draw.text(position, first_letter, fill=(255, 255, 255), font=font)

            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            self.avatar.save(f'avatar_{random.randint(1000, 9999)}.png',
                             ContentFile(buffer.getvalue()), save=False)

        if self.phone and self.phone.startswith('8'):
            self.phone = '+7' + self.phone[1:]

        super().save(*args, **kwargs)
