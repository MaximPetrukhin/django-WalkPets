from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserLoginForm, UserRegistrationForm, UserProfileForm
from django.core.files.storage import default_storage
from django.core.exceptions import PermissionDenied


def login(request):
    """Обработка входа пользователя"""
    if request.user.is_authenticated:
        return redirect('users:profile')

    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                auth_login(request, user)
                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(0)
                messages.success(request, f'Добро пожаловать, {username}!')
                next_url = request.GET.get('next', 'users:profile')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')

        return render(request, "users/login.html", {'form': form})

    return render(request, "users/login.html", {'form': UserLoginForm()})


def register(request):
    """Обработка регистрации нового пользователя"""
    if request.user.is_authenticated:
        return redirect('users:profile')

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                auth_login(request, user)
                messages.success(request, "Вы успешно зарегистрировались!")
                return redirect('users:profile')
            except Exception as e:
                messages.error(request, f'Ошибка при регистрации: {str(e)}')
        return render(request, "users/register.html", {'form': form})

    return render(request, "users/register.html", {'form': UserRegistrationForm()})


@login_required
def profile(request):
    """Редактирование профиля пользователя"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)

        if 'delete_avatar' in request.POST:
            try:
                if request.user.image:
                    default_storage.delete(request.user.image.path)
                    request.user.image = None
                    request.user.save()
                    messages.success(request, 'Аватар успешно удалён!')
            except Exception as e:
                messages.error(request, f'Ошибка при удалении аватара: {str(e)}')
            return redirect('users:profile')

        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Профиль успешно обновлён!')
                return redirect('users:profile')
            except Exception as e:
                messages.error(request, f'Ошибка при обновлении профиля: {str(e)}')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')

        return render(request, 'users/profile.html', {'form': form})

    form = UserProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})


def logout(request):
    """Выход пользователя из системы"""
    if not request.user.is_authenticated:
        raise PermissionDenied
    auth_logout(request)
    messages.info(request, 'Вы успешно вышли из системы')
    return redirect('index')