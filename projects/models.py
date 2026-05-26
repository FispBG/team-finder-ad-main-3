from django.db import models
from django.conf import settings


class Project(models.Model):
    """Модель для представления проекта в системе."""

    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
    ]
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE, related_name='owned_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default="open")
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                          blank=True, related_name='participated_projects')
    skills = models.ManyToManyField('users.Skill', blank=True, related_name='projects')

    def __str__(self):
        return str(self.name)

    class Meta:
        """Устанавливаем порядок сортировки проектов по дате создания, от новых к старым."""

        ordering = ['-created_at']
