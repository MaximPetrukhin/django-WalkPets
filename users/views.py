from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.exceptions import PermissionDenied
from .forms import UserLoginForm, UserRegistrationForm, UserProfileForm, ReviewForm
from .models import Review, User
from django.shortcuts import get_object_or_404, redirect

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
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)

        if 'delete_avatar' in request.POST:
            if request.user.image:
                default_storage.delete(request.user.image.path)
                request.user.image = None
                request.user.save()
                messages.success(request, 'Аватар удалён!')
            return redirect('users:profile')

        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён!')
            return redirect('users:profile')
        return render(request, 'users/profile.html', {'form': form})

    form = UserProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})


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
        form = ReviewForm()

    return render(request, 'users/create_review.html', {'form': form})


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Проверяем, является ли пользователь автором отзыва или суперпользователем
    if not (request.user == review.author or request.user.is_superuser):
        raise PermissionDenied("Вы не можете удалить этот отзыв")

    review.delete()
    messages.success(request, 'Отзыв успешно удален!')
    return redirect('users:reviews')


def reviews_list(request):
    reviews = Review.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'users/reviews_list.html', {'reviews': reviews})


def top_reviews(request):
    top_reviews = Review.objects.filter(
        is_published=True,
        rating__gte=4
    ).order_by('-created_at')[:5]
    return {'top_reviews': top_reviews}


def logout(request):
    auth_logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('index')