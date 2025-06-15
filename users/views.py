from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.exceptions import PermissionDenied
from .forms import UserLoginForm, UserRegistrationForm, UserProfileForm, ReviewForm
from .models import Review
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model


User = get_user_model()



def login(request):
    if request.user.is_authenticated:
        return redirect('users:profile')

    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user:
                auth_login(request, user)
                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(0)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('users:profile')

        messages.error(request, 'Неверное имя пользователя или пароль')
        return render(request, "users/login.html", {'form': form})

    return render(request, "users/login.html", {'form': UserLoginForm()})


def register(request):
    if request.user.is_authenticated:
        return redirect('users:profile')

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Вы успешно зарегистрировались!")
            return redirect('users:profile')
        return render(request, "users/register.html", {'form': form})

    return render(request, "users/register.html", {'form': UserRegistrationForm()})


@login_required
def profile(request):
    user = request.user

    if request.method == 'POST':
        if 'delete_avatar' in request.POST:
            if user.image:
                default_storage.delete(user.image.path)
                user.image = None
                user.save()
                messages.success(request, 'Аватар удалён!')
            return redirect('users:profile')

        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            # Явно сохраняем дату рождения
            user.birth_date = form.cleaned_data['birth_date']
            user.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'users/profile.html', {
        'form': form,
        'user': user
    })


@login_required
def create_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.save()
            messages.success(request, 'Ваш отзыв успешно опубликован!')
            return redirect('users:reviews')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = ReviewForm()

    return render(request, 'users/create_review.html', {'form': form})


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if not (request.user == review.author or request.user.is_superuser):
        raise PermissionDenied("Вы не можете удалить этот отзыв")

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Отзыв успешно удалён!')
        return redirect('users:reviews')

    return render(request, 'users/confirm_delete.html', {'review': review})


def reviews_list(request):
    reviews = Review.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'users/reviews_list.html', {'reviews': reviews})


def logout(request):
    auth_logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('index')