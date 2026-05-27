# Сторонние библиотеки
from django.contrib import admin

# Локальные импорты
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Админка для управления проектами."""

    list_display = ('name', 'owner', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description', 'owner__email')
    ordering = ('-created_at',)
