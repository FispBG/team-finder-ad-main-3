# Сторонние библиотеки
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """Менеджер для модели User, обеспечивающий создание пользователей и суперпользователей."""

    def create_user(self, email, name, surname, password=None, **extra_fields):
        """Создает и сохраняет пользователя с указанными данными."""
        if not email:
            raise ValueError("Email является обязательным полем")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        """Создает и сохраняет суперпользователя с указанными данными."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, name, surname, password, **extra_fields)
