# Стандартные библиотеки
from http import HTTPStatus
import json

# Сторонние библиотеки
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth import get_user_model

# Локальные импорты
from .models import Skill
from .forms import RegistrationForm, LoginForm, ProfileEditForm, PasswordChangeForm
from projects.models import Project

User = get_user_model()

FILTER_OWNERS_FAVORITE = 'owners-of-favorite-projects'
FILTER_OWNERS_PARTICIPATING = 'owners-of-participating-projects'
FILTER_INTERESTED_MY = 'interested-in-my-projects'
FILTER_PARTICIPANTS_MY = 'participants-of-my-projects'

MAX_AUTOCOMPLETE_RESULTS = 10


def get_paginated_page(request, queryset, per_page=12):
    """Вспомогательная функция для пагинации."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def user_list(request):
    """Отображение списка пользователей."""
    users_qs = User.objects.prefetch_related('skills').order_by('-id')
    active_filter = request.GET.get('filter')
    active_skill = request.GET.get('skill')

    if active_filter and request.user.is_authenticated:
        if active_filter == FILTER_OWNERS_FAVORITE:
            users_qs = users_qs.filter(owned_projects__interested_users=request.user).distinct()
        elif active_filter == FILTER_OWNERS_PARTICIPATING:
            users_qs = users_qs.filter(owned_projects__participants=request.user).distinct()
        elif active_filter == FILTER_INTERESTED_MY:
            users_qs = users_qs.filter(favorites__owner=request.user).distinct()
        elif active_filter == FILTER_PARTICIPANTS_MY:
            users_qs = users_qs.filter(participated_projects__owner=request.user).distinct()

    if active_skill:
        users_qs = users_qs.filter(skills__name=active_skill).distinct()

    participants = get_paginated_page(request, users_qs)
    all_skills = Skill.objects.all()

    context = {
        'participants': participants,
        'active_filter': active_filter,
        'skills': all_skills,
        'active_skill': active_skill
    }
    return render(request, 'users/participants.html', context)


def user_details(request, pk):
    """Отображение деталей пользователя по его ID."""
    user_obj = get_object_or_404(User, pk=pk)
    return render(request, 'users/user-details.html', {'user': user_obj})


def register_view(request):
    """Регистрация нового пользователя."""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('projects:project_list')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """Вход пользователя в систему."""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('projects:project_list')
            else:
                form.add_error(None, "Неверный имейл или пароль")
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def edit_profile(request):
    """Редактирование профиля пользователя."""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:user_details', pk=request.user.id)
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    """Смена пароля для текущего пользователя."""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password1'])
            request.user.save()
            login(request, request.user)
            return redirect('users:user_details', pk=request.user.id)
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'users/change_password.html', {'form': form})


def logout_view(request):
    """Выход пользователя из системы."""
    logout(request)
    return redirect('projects:project_list')


def skill_autocomplete(request, mode):
    """Автодополнение навыков для проектов и пользователей."""
    search_query = request.GET.get('q', '').strip()
    skills = Skill.objects.filter(name__istartswith=search_query)[:MAX_AUTOCOMPLETE_RESULTS]
    data = [{"id": s.id, "name": s.name} for s in skills]
    return JsonResponse(data, safe=False)


@login_required
def add_skill(request, mode, pk):
    """Добавление навыка к проекту или пользователю."""
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            data = request.POST

        skill_id = data.get('skill_id')
        name = data.get('name', '').strip()
        created, skill = False, None

        if skill_id:
            skill = Skill.objects.filter(id=skill_id).first()
        elif name:
            skill, created = Skill.objects.get_or_create(name=name)

        if not skill:
            return JsonResponse({"error": "No skill info provided"}, status=HTTPStatus.BAD_REQUEST)

        added = False
        if mode == 'projects':
            project = Project.objects.filter(pk=pk).first()
            if not project:
                return JsonResponse({"error": "Project not found"}, status=HTTPStatus.NOT_FOUND)

            if project.owner != request.user:
                return JsonResponse({"error": "Forbidden"}, status=HTTPStatus.FORBIDDEN)
            if not project.skills.filter(id=skill.id).exists():
                project.skills.add(skill)
                added = True

        elif mode == 'users':
            if int(pk) != request.user.id:
                return JsonResponse({"error": "Forbidden"}, status=HTTPStatus.FORBIDDEN)
            if not request.user.skills.filter(id=skill.id).exists():
                request.user.skills.add(skill)
                added = True

        return JsonResponse({"skill_id": skill.id, "created": created, "added": added})
    return JsonResponse({"error": "Method not allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED)


@login_required
def remove_skill(request, mode, pk, skill_id):
    """Удаление навыка из проекта или пользователя."""
    if request.method == "POST":
        skill = Skill.objects.filter(id=skill_id).first()
        if not skill:
            return JsonResponse({"error": "Skill not found"}, status=HTTPStatus.NOT_FOUND)

        if mode == 'projects':
            project = Project.objects.filter(pk=pk).first()
            if not project:
                return JsonResponse({"error": "Project not found"}, status=HTTPStatus.NOT_FOUND)

            if project.owner != request.user:
                return JsonResponse({"error": "Forbidden"}, status=HTTPStatus.FORBIDDEN)
            if project.skills.filter(id=skill.id).exists():
                project.skills.remove(skill)

        elif mode == 'users':
            if int(pk) != request.user.id:
                return JsonResponse({"error": "Forbidden"}, status=HTTPStatus.FORBIDDEN)
            if skill in request.user.skills.filter(id=skill.id).exists():
                request.user.skills.remove(skill)
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "Method not allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED)
