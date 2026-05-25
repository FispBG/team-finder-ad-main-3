from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Project, Skill


class UserAdmin(BaseUserAdmin):
    """Настройка отображения кастомной модели пользователя в админке."""

    list_display = ('email', 'name', 'surname', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личные данные', {'fields': ('name', 'surname',
                                      'avatar', 'phone', 'github_url', 'about')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff',
                                      'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'surname', 'password'),
        }),
    )

    search_fields = ('email', 'name', 'surname')
    ordering = ('-id',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Настройка отображения модели проекта в админке."""

    list_display = ('name', 'owner', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description', 'owner__email')
    ordering = ('-created_at',)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Настройка отображения модели навыков в админке."""

    list_display = ('name',)
    search_fields = ('name',)
