from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from users import views as user_views
from django.conf import settings
from django.conf.urls.static import static


def root_redirect(request):
    """Перенаправление с корневого URL на список проектов."""
    return redirect("/projects/list/")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", root_redirect, name="root_redirect"),
    path("users/", include("users.urls", namespace="users")),
    path("projects/", include("projects.urls", namespace="projects")),
    path(
        "<str:mode>/skills/", user_views.skill_autocomplete, name="skill_autocomplete"
    ),
    path("<str:mode>/<int:pk>/skills/add", user_views.add_skill, name="add_skill"),
    path(
        "<str:mode>/<int:pk>/skills/<int:skill_id>/remove/",
        user_views.remove_skill,
        name="remove_skill",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
