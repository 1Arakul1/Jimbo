from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from .forms import LoginForm, RegisterForm, EditProfileForm, PasswordResetRequestForm
from dogs.models import Dog
import secrets
from users.models import User  # Импортируйте свою модель пользователя

@login_required
def user_profile(request):
    """Представление для просмотра профиля пользователя."""
    title = 'Профиль пользователя'
    user = request.user
    dogs = Dog.objects.filter(owner=user)
    context = {'title': title, 'user': user, 'dogs': dogs}
    return render(request, 'users/user_profile.html', context)

@login_required
def edit_profile(request):
    """Представление для редактирования профиля пользователя."""
    title = 'Редактировать профиль'
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:user_profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = EditProfileForm(instance=request.user)
    context = {'title': title, 'form': form}
    return render(request, 'users/edit_profile.html', context)

@login_required
def change_password(request):
    """Представление для смены пароля пользователя."""
    title = 'Сменить пароль'
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Сохраняем сессию
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('users:user_profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = PasswordChangeForm(request.user)
    context = {'title': title, 'form': form}
    return render(request, 'users/change_password.html', context)

def user_login(request):
    """Представление для входа пользователя."""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('users:welcome')  # Перенаправляем на страницу приветствия
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

def register(request):
    """Представление для регистрации нового пользователя."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()

                # Генерация и отправка письма с подтверждением регистрации
                subject = 'Добро пожаловать в наш питомник!'
                message = f'Здравствуйте, {user.username}!\n\nСпасибо за регистрацию в нашем питомнике.'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [user.email]

                email = EmailMessage(subject, message, from_email, recipient_list)
                email.fail_silently = False
                email.send()

                messages.success(request, "Вы успешно зарегистрировались и вошли в систему!")
                login(request, user)  # Автоматический вход
                return redirect('users:welcome')  # Перенаправляем на страницу приветствия
            except Exception as e:
                messages.error(request, f"Ошибка при регистрации: {str(e)}")
        else:
            # Больше не нужно перебирать form.errors, они отображаются в шаблоне
            pass
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def logout(request):
    """Представление для выхода пользователя."""
    django_logout(request)
    return redirect('users:logout_success')  # Перенаправляем на страницу выхода

def password_reset_request(request):
    """Представление для запроса сброса пароля."""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                # Поиск пользователя по email. Используем свою модель User
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "Пользователь с таким email не найден.")
                return render(request, 'users/password_reset_request.html', {'form': form})

            # Генерация случайного пароля
            new_password = secrets.token_urlsafe(16)

            # Установка нового пароля для пользователя
            user.set_password(new_password)
            user.save()

            # Отправка письма с новым паролем
            subject = 'Сброс пароля для вашего аккаунта'
            message = render_to_string(
                'users/password_reset_email.html',
                {'user': user, 'new_password': new_password}
            )
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.fail_silently = False
            email.send()

            messages.success(request, "На ваш email отправлено письмо с новым паролем.")
            return redirect('dogs:index')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = PasswordResetRequestForm()
    return render(request, 'users/password_reset_request.html', {'form': form})

# Новые представления для приветствия и выхода
@login_required  # Необязательно, но логично, чтобы увидеть приветствие после входа
def welcome(request):
    """Страница приветствия после входа."""
    return render(request, 'users/welcome.html', {'user': request.user})


def logout_success(request):
    """Страница после выхода."""
    return render(request, 'users/logout_success.html')





