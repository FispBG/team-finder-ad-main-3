# Стандартные библиотеки
from http import HTTPStatus

# Сторонние библиотеки
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden

# Локальные импорты
from .models import STATUS_CLOSED, STATUS_OPEN, Project
from .forms import ProjectForm
from users.models import Skill


def get_paginated_page(request, queryset, per_page=12):
    """Вспомогательная функция для пагинации."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def project_list(request):
    """Отображение списка проектов с возможностью фильтрации по навыкам."""
    projects_qs = Project.objects.select_related('owner').prefetch_related('skills')
    active_skill = request.GET.get('skill')

    if active_skill:
        projects_qs = projects_qs.filter(skills__name=active_skill).distinct()

    page_obj = get_paginated_page(request, projects_qs)
    all_skills = Skill.objects.all()

    context = {
        'projects': page_obj,
        'skills': all_skills,
        'active_skill': active_skill
    }
    return render(request, 'projects/project_list.html', context)


@login_required
def favorite_projects(request):
    """Отображение списка избранных проектов текущего пользователя."""
    projects_qs = request.user.favorites.all()
    return render(request, 'projects/favorite_projects.html', {'projects': projects_qs})


def project_details(request, pk):
    """Отображение деталей проекта по его ID."""
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projects/project-details.html', {'project': project})


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
            return redirect('projects:project_details', pk=project.id)
    else:
        form = ProjectForm()
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': False})


@login_required
def edit_project(request, pk):
    """Редактирование существующего проекта. Доступно только для автора проекта."""
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        return HttpResponseForbidden("Вы не являетесь автором проекта")
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('projects:project_details', pk=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})


@login_required
def complete_project(request, pk):
    """Отметить проект как завершенный. Доступно только для автора проекта."""
    if request.method == "POST":
        project = Project.objects.filter(pk=pk).first()
        if project is None:
            return JsonResponse({"error": "Project not found"}, status=HTTPStatus.NOT_FOUND)
        if project.owner != request.user:
            return JsonResponse({"error": "Вы не являетесь автором проекта"},
                                status=HTTPStatus.FORBIDDEN)
        if project.status == STATUS_OPEN:
            project.status = STATUS_CLOSED
            project.save()
        return JsonResponse({"status": "ok", "project_status": STATUS_CLOSED})

    return JsonResponse({"error": "Method not allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED)


def toggle_favorite(request, project_id):
    """Добавление или удаление проекта из избранного текущего пользователя."""
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Unauthorized"},
                            status=HTTPStatus.UNAUTHORIZED)

    if request.method == "POST":
        project = Project.objects.filter(id=project_id).first()
        if project is None:
            return JsonResponse({"error": "Project not found"}, status=HTTPStatus.NOT_FOUND)

        user = request.user
        is_favorited = user.favorites.filter(id=project.id).exists()
        if is_favorited:
            user.favorites.remove(project)
        else:
            user.favorites.add(project)

        return JsonResponse({"status": "ok", "favorited": not is_favorited})
    return JsonResponse({"error": "Method not allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED)


def toggle_participate(request, pk):
    """Добавление или удаление текущего пользователя из участников проекта."""
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Unauthorized"},
                            status=HTTPStatus.UNAUTHORIZED)

    if request.method == "POST":
        project = Project.objects.filter(pk=pk).first()
        if project is None:
            return JsonResponse({"error": "Project not found"}, status=HTTPStatus.NOT_FOUND)

        if project.owner == request.user:
            return JsonResponse({"error": "Owner cannot leave/join via toggle"},
                                status=HTTPStatus.BAD_REQUEST)

        is_active = project.participants.filter(id=request.user.id).exists()

        if is_active:
            project.participants.remove(request.user)
        else:
            project.participants.add(request.user)

        return JsonResponse({"status": "ok", "participant": not is_active})
    return JsonResponse({"error": "Method not allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED)
