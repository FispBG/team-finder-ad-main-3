from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import get_user_model
import json

from .models import Project, Skill
from .forms import RegistrationForm, LoginForm, ProfileEditForm, PasswordChangeForm, ProjectForm

User = get_user_model()


def root_redirect(request):
    """Перенаправление с корневого URL на страницу со списком проектов."""
    return redirect('/projects/list/')


def project_list(request):
    """Просмотр списка проектов с возможностью фильтрации по навыкам."""
    projects_qs = Project.objects.all()
    active_skill = request.GET.get('skill')

    if active_skill:
        projects_qs = projects_qs.filter(skills__name=active_skill).distinct()

    paginator = Paginator(projects_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    all_skills = Skill.objects.all()

    context = {
        'projects': page_obj,
        'skills': all_skills,
        'active_skill': active_skill
    }
    return render(request, 'projects/project_list.html', context)


def toggle_favorite(request, project_id):
    """Переключение статуса избранного проекта для авторизованных пользователей."""
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=401)

    if request.method == "POST":
        project = get_object_or_404(Project, id=project_id)
        user = request.user
        if project in user.favorites.all():
            user.favorites.remove(project)
            favorited = False
        else:
            user.favorites.add(project)
            favorited = True
        return JsonResponse({"status": "ok", "favorited": favorited})
    return JsonResponse({"error": "Method not allowed"}, status=405)


def user_list(request):
    """Просмотр списка пользователей с возможностью фильтрации по различным критериям."""
    users_qs = User.objects.all().order_by('-id')
    active_filter = request.GET.get('filter')
    active_skill = request.GET.get('skill')

    if active_filter and request.user.is_authenticated:
        if active_filter == 'owners-of-favorite-projects':
            users_qs = users_qs.filter(owned_projects__interested_users=request.user).distinct()
        elif active_filter == 'owners-of-participating-projects':
            users_qs = users_qs.filter(owned_projects__participants=request.user).distinct()
        elif active_filter == 'interested-in-my-projects':
            users_qs = users_qs.filter(favorites__owner=request.user).distinct()
        elif active_filter == 'participants-of-my-projects':
            users_qs = users_qs.filter(participated_projects__owner=request.user).distinct()

    if active_skill:
        users_qs = users_qs.filter(skills__name=active_skill).distinct()

    paginator = Paginator(users_qs, 12)
    page_number = request.GET.get('page')
    participants = paginator.get_page(page_number)

    all_skills = Skill.objects.all()

    context = {
        'participants': participants,
        'active_filter': active_filter,
        'skills': all_skills,
        'active_skill': active_skill
    }
    return render(request, 'users/participants.html', context)


@login_required
def favorite_projects(request):
    """Просмотр избранных проектов текущего пользователя."""
    projects_qs = request.user.favorites.all()
    return render(request, 'projects/favorite_projects.html', {'projects': projects_qs})


def project_details(request, pk):
    """Просмотр деталей проекта.

    Доступно для всех, но отображает больше информации для авторизованных пользователей.
    """
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projects/project-details.html', {'project': project})


@login_required
def complete_project(request, pk):
    """Завершение проекта. Доступно только для владельца проекта."""
    if request.method == "POST":
        project = get_object_or_404(Project, pk=pk)
        if project.owner != request.user:
            return HttpResponseForbidden("Вы не являетесь автором проекта")
        if project.status == "open":
            project.status = "closed"
            project.save()
        return JsonResponse({"status": "ok", "project_status": "closed"})
    return JsonResponse({"error": "Method not allowed"}, status=405)


def toggle_participate(request, pk):
    """Переключение участия в проекте для авторизованных пользователей."""
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=401)

    if request.method == "POST":
        project = get_object_or_404(Project, pk=pk)

        if project.owner == request.user:
            return JsonResponse({"error": "Owner cannot leave/join via toggle"}, status=400)

        if project.participants.filter(id=request.user.id).exists():
            project.participants.remove(request.user)
            is_active = False
        else:
            project.participants.add(request.user)
            is_active = True

        return JsonResponse({
            "status": "ok",
            "participant": is_active
        })

    return JsonResponse({"error": "Method not allowed"}, status=405)


def skill_autocomplete(request, mode):
    """Автодополнение навыков при добавлении в проект или профиль пользователя."""
    q = request.GET.get('q', '').strip()
    skills = Skill.objects.filter(name__istartswith=q)[:10]
    data = [{"id": s.id, "name": s.name} for s in skills]
    return JsonResponse(data, safe=False)


@login_required
def add_skill(request, mode, pk):
    """Добавление навыка к проекту или профилю пользователя."""
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            data = request.POST

        skill_id = data.get('skill_id')
        name = data.get('name', '').strip()

        created = False
        skill = None

        if skill_id:
            skill = get_object_or_404(Skill, id=skill_id)
        elif name:
            skill, created = Skill.objects.get_or_create(name=name)

        if not skill:
            return JsonResponse({"error": "No skill info provided"}, status=400)

        added = False
        if mode == 'projects':
            project = get_object_or_404(Project, pk=pk)
            if project.owner != request.user:
                return HttpResponseForbidden()
            if skill not in project.skills.all():
                project.skills.add(skill)
                added = True
        elif mode == 'users':
            if int(pk) != request.user.id:
                return HttpResponseForbidden()
            if skill not in request.user.skills.all():
                request.user.skills.add(skill)
                added = True

        return JsonResponse({"skill_id": skill.id, "created": created, "added": added})
    return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required
def remove_skill(request, mode, pk, skill_id):
    """Удаление навыка из проекта или профиля пользователя."""
    if request.method == "POST":
        skill = get_object_or_404(Skill, id=skill_id)
        if mode == 'projects':
            project = get_object_or_404(Project, pk=pk)
            if project.owner != request.user:
                return HttpResponseForbidden()
            if skill in project.skills.all():
                project.skills.remove(skill)
        elif mode == 'users':
            if int(pk) != request.user.id:
                return HttpResponseForbidden()
            if skill in request.user.skills.all():
                request.user.skills.remove(skill)
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "Method not allowed"}, status=405)


def user_details(request, pk):
    """Просмотр профиля пользователя.

    Доступно для всех, но отображает больше информации для авторизованных пользователей.
    """
    user_obj = get_object_or_404(User, pk=pk)
    return render(request, 'users/user-details.html', {'user': user_obj})


def register_view(request):
    """Регистрация нового пользователя."""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/projects/list/')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """Авторизация пользователя.

    При успешной авторизации перенаправление на страницу со списком проектов.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('/projects/list/')
            else:
                form.add_error(None, "Неверный имейл или пароль")
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def edit_profile(request):
    """Редактирование профиля для авторизованных пользователей.

    Доступно только для владельца профиля.
    """
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(f'/users/{request.user.id}/')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    """Смена пароля для авторизованных пользователей.

    После успешной смены пользователь остается авторизованным.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password1'])
            request.user.save()
            login(request, request.user)
            return redirect(f'/users/{request.user.id}/')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'users/change_password.html', {'form': form})


def logout_view(request):
    """Выход из аккаунта и перенаправление на страницу со списком проектов."""
    logout(request)
    return redirect('/projects/list/')


@login_required
def create_project(request):
    """Создание нового проекта. Доступно только для авторизованных пользователей."""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(f'/projects/{project.id}/')
    else:
        form = ProjectForm()
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': False})


@login_required
def edit_project(request, pk):
    """Редактирование проекта. Доступно только для владельца проекта."""
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        return HttpResponseForbidden("Вы не являетесь автором проекта")
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(f'/projects/{project.id}/')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})
