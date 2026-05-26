from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden

from .models import Project
from .forms import ProjectForm
from users.models import Skill


def project_list(request):
    """Отображение списка проектов с возможностью фильтрации по навыкам."""
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
            return redirect(f'/projects/{project.id}/')
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
            return redirect(f'/projects/{project.id}/')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})


@login_required
def complete_project(request, pk):
    """Отметить проект как завершенный. Доступно только для автора проекта."""
    if request.method == "POST":
        project = get_object_or_404(Project, pk=pk)
        if project.owner != request.user:
            return HttpResponseForbidden("Вы не являетесь автором проекта")
        if project.status == "open":
            project.status = "closed"
            project.save()
        return JsonResponse({"status": "ok", "project_status": "closed"})
    return JsonResponse({"error": "Method not allowed"}, status=405)


def toggle_favorite(request, project_id):
    """Добавление или удаление проекта из избранного текущего пользователя."""
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


def toggle_participate(request, pk):
    """Добавление или удаление текущего пользователя из участников проекта."""
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
        return JsonResponse({"status": "ok", "participant": is_active})
    return JsonResponse({"error": "Method not allowed"}, status=405)
