from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import LoginForm, RegisterForm, EditProfileForm
from dogs.models import Dog
from django.core.mail import send_mail, EmailMessage  # Импортируем EmailMessage
from django.conf import settings

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
            update_session_auth_hash(request, user)
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
                return redirect('dogs:index')
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

                subject = 'Добро пожаловать в наш питомник!'
                message = f'Здравствуйте, {user.username}!\n\nСпасибо за регистрацию в нашем питомнике.'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [user.email]

                # Используем EmailMessage для большей гибкости и отладки
                email = EmailMessage(subject, message, from_email, recipient_list)
                email.fail_silently = False  # Важно для отладки
                email.send()

                print("Письмо успешно отправлено!")  # Сообщение об успешной отправке

                login(request, user)  # Автоматический вход
                messages.success(request, "Вы успешно зарегистрировались и вошли в систему!")  # Сообщение об успехе
                return redirect('dogs:index')
            except Exception as e:
                error_message = f"Ошибка при отправке письма: {type(e).__name__} - {str(e)}"
                print(error_message)
                messages.error(request, f"Ошибка при регистрации: {error_message}")  # Более информативное сообщение об ошибке
        else:
            for field, errors in form.errors.items():  # Вывод ошибок для каждого поля
                for error in errors:
                    messages.error(request, f"Ошибка в поле {form.fields[field].label if field in form.fields else field}: {error}")
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def logout(request):
    """Представление для выхода пользователя."""
    django_logout(request)
    return redirect('dogs:index')
