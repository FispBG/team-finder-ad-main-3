# Сторонние библиотеки
from django.urls import path

# Локальные импорты
from . import views

app_name = 'users'

urlpatterns = [
    path('list/', views.user_list, name='user_list'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('<int:pk>/', views.user_details, name='user_details'),
]
