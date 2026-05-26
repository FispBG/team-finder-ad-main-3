from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Конфигурация приложения для управления пользователями."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
