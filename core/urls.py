from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.root_redirect, name='root_redirect'),

    path('projects/list/', views.project_list, name='project_list'),
    path('projects/favorites/', views.favorite_projects, name='favorite_projects'),
    path('projects/create-project/', views.create_project, name='create_project'),
    path('projects/<int:pk>/', views.project_details, name='project_details'),
    path('projects/<int:pk>/edit/', views.edit_project, name='edit_project'),

    path('projects/<int:project_id>/toggle-favorite/',
         views.toggle_favorite,
         name='toggle_favorite'),

    path('projects/<int:pk>/complete/', views.complete_project, name='complete_project'),

    path('projects/<int:pk>/toggle-participate/',
         views.toggle_participate,
         name='toggle_participate'),

    path('users/list/', views.user_list, name='user_list'),
    path('users/register/', views.register_view, name='register'),
    path('users/login/', views.login_view, name='login'),
    path('users/logout/', views.logout_view, name='logout'),
    path('users/edit-profile/', views.edit_profile, name='edit_profile'),
    path('users/change-password/', views.change_password, name='change_password'),
    path('users/<int:pk>/', views.user_details, name='user_details'),

    path('<str:mode>/skills/', views.skill_autocomplete, name='skill_autocomplete'),
    path('<str:mode>/<int:pk>/skills/add', views.add_skill, name='add_skill'),
    path('<str:mode>/<int:pk>/skills/<int:skill_id>/remove/',
         views.remove_skill,
         name='remove_skill'),
]
