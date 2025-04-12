from django.urls import path
from . import views  # Импортируем ваши views
from . import views_reset_password  # Импортируем views_reset_password

app_name = 'users'

urlpatterns = [
    path('profile/', views.user_profile, name='user_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('password_reset/', views_reset_password.password_reset_request, name='password_reset_request'),  # Добавлен URL
]