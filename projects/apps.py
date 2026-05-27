# Сторонние библиотеки
from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    """Конфигурация приложения для управления проектами."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects'
