# Сторонние библиотеки
from django.db import models
from django.conf import settings

PROJECT_NAME_MAX_LENGTH = 200
PROJECT_STATUS_MAX_LENGTH = 6

STATUS_OPEN = "open"
STATUS_CLOSED = "closed"

PROJECT_STATUS_CHOICES = [
    (STATUS_OPEN, "Open"),
    (STATUS_CLOSED, "Closed"),
]


class Project(models.Model):
    """Модель для представления проекта в системе."""

    name = models.CharField(max_length=PROJECT_NAME_MAX_LENGTH)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=PROJECT_STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="participated_projects"
    )
    skills = models.ManyToManyField("users.Skill", blank=True, related_name="projects")

    class Meta:
        """Устанавливаем порядок сортировки проектов по дате создания, от новых к старым."""

        ordering = ["-created_at"]

    def __str__(self):
        return str(self.name)
