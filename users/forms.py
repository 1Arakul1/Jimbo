from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from .models import User  # Важно: импортируем вашу кастомную модель!
from django.core.exceptions import ValidationError

class LoginForm(AuthenticationForm):
    """
    Форма для входа пользователя.
    Использует AuthenticationForm из django.contrib.auth.forms для обработки аутентификации.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Пароль')


class RegisterForm(forms.Form):
    """
    Форма для регистрации нового пользователя.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Имя пользователя')
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Пароль')
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Подтвердите пароль')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем класс 'form-control' ко всем полям формы
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_username(self):
        """
        Проверяет, что имя пользователя еще не занято.
        """
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Это имя пользователя уже занято.")
        return username

    def clean_email(self):
        """
        Проверяет, что email еще не занят.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже зарегистрирован.")
        return email

    def clean_password(self):
        """
        Проверяет минимальную длину пароля.
        """
        password = self.cleaned_data.get('password')
        if len(password) < 8:  # Например, минимальная длина - 8 символов
            raise forms.ValidationError("Пароль должен содержать не менее 8 символов.")
        return password

    def clean(self):
        """
        Проверяет, что пароль и подтверждение пароля совпадают.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("password_confirm")

        if password and confirm_password:  # убеждаемся, что оба поля заполнены
            if password != confirm_password:
                self.add_error('password_confirm', "Пароли не совпадают.") # Привязываем ошибку к полю "password_confirm"
        return cleaned_data

    def save(self):
        """
        Сохраняет нового пользователя.
        """
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        user = User.objects.create_user(username=username, email=email, password=password)

        return user


class EditProfileForm(UserChangeForm):
    """
    Форма для редактирования профиля пользователя.
    Наследуется от UserChangeForm и позволяет изменять email. Удалены first_name и last_name.
    """
    password = None  # Убираем поле password из формы

    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем help_text для полей (необязательно)
        self.fields['email'].help_text = None

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254, widget=forms.EmailInput(attrs={'class': 'form-control'}))