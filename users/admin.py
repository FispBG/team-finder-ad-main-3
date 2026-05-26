from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Skill


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для управления пользователями."""

    list_display = ('email', 'name', 'surname', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личные данные', {'fields': ('name', 'surname', 'avatar',
                                      'phone', 'github_url', 'about')}),
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


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Админка для управления навыками."""

    list_display = ('name',)
    search_fields = ('name',)
