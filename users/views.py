from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.files.storage import default_storage
from .forms import UserLoginForm, UserRegistrationForm, UserProfileForm
from django.utils import timezone


def login(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user:
                auth_login(request, user)
                if not form.cleaned_data.get('remember'):
                    request.session.set_expiry(0)  # Сессия закончится при закрытии браузера
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('users:profile')

        messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, "users/login.html", {
        'form': UserLoginForm()
    })


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Вы успешно зарегистрировались!")
            return redirect('index')

    return render(request, "users/register.html", {
        'form': UserRegistrationForm()
    })



@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'users/profile.html', {
        'form': form,
        'now': timezone.now().date()
    })


def logout(request):
    auth_logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('index')


@login_required
def upload_avatar(request):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            if request.user.image:
                # Удаляем старый аватар
                request.user.image.delete(save=False)

            # Сохраняем новый аватар
            request.user.image = request.FILES['image']
            request.user.save()

            return JsonResponse({
                'status': 'success',
                'avatar_url': request.user.image.url
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    return JsonResponse({
        'status': 'error',
        'message': 'Неверный запрос'
    }, status=400)


@login_required
def delete_avatar(request):
    try:
        user = request.user

        if not user.image:
            return JsonResponse({
                'success': False,
                'error': 'Аватар не найден'
            }, status=404)

        # Удаляем файл и очищаем поле
        user.image.delete(save=False)
        user.image = None
        user.save()

        return JsonResponse({
            'success': True,
            'initials': user.get_initials(),
            'message': 'Аватар успешно удалён'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)