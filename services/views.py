from django.shortcuts import render, get_object_or_404
from .models import ServicesCategory, Services, Walker
from users.models import Review  # Импортируем модель отзывов
from users.forms import ReviewForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .forms import WalkerApplicationForm
from django.contrib import messages
from django.db import models
from django.core.paginator import Paginator


def index(request):
    """Главная страница сайта - только отзывы о сайте"""
    site_reviews = Review.objects.filter(
        review_type='site',
        is_published=True,
        rating__gte=4
    ).select_related('author').order_by('-created_at')[:3]

    return render(request, 'services/index.html', {
        'top_reviews': site_reviews
    })


def service_list(request):
    """Список всех услуг"""
    services = Services.objects.filter(is_active=True)
    return render(request, 'services/services.html', {'services': services})


def category_list(request):
    """Список категорий услуг"""
    categories = ServicesCategory.objects.all()
    return render(request, 'services/categories.html', {'categories': categories})


def category_detail(request, slug):
    """Детальная страница категории"""
    category = get_object_or_404(ServicesCategory, slug=slug)
    services = Services.objects.filter(category=category, is_active=True)
    walkers = Walker.objects.filter(status='approved')[:5]
    similar_services = Services.objects.filter(category=category, is_active=True).exclude(
        id__in=[s.id for s in services])[:3]

    return render(request, 'services/category_detail.html', {
        'category': category,
        'services': services,
        'walkers': walkers,
        'similar_services': similar_services
    })


def service_detail(request, service_id):
    """Детальная страница услуги"""
    service = get_object_or_404(Services, id=service_id, is_active=True)
    return render(request, 'services/service_detail.html', {'service': service})


def walker_list(request):
    """Список всех выгульщиков"""
    walkers = Walker.objects.filter(status='approved')
    return render(request, 'services/walker_list.html', {'walkers': walkers})


def walker_detail(request, walker_id):
    walker = get_object_or_404(Walker, id=walker_id, status='approved')

    # Получаем все отзывы с пагинацией
    all_reviews = Review.objects.filter(
        walker=walker,
        review_type='walker',
        is_published=True
    ).select_related('author').order_by('-created_at')

    paginator = Paginator(all_reviews, 5)  # 5 отзывов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Получаем отзыв текущего пользователя
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(
            author=request.user,
            walker=walker
        ).first()

    # Обработка формы отзыва
    if request.method == 'POST' and request.user.is_authenticated:
        if user_review:
            messages.error(request, 'Вы уже оставили отзыв этому выгульщику')
            return redirect('services:walker_detail', walker_id=walker.id)

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.walker = walker
            review.review_type = 'walker'
            review.save()

            # Обновляем рейтинг выгульщика
            walker.update_rating()

            messages.success(request, 'Ваш отзыв успешно сохранен!')
            return redirect('services:walker_detail', walker_id=walker.id)
    else:
        form = ReviewForm(instance=user_review) if user_review else ReviewForm()

    return render(request, 'services/walker_detail.html', {
        'walker': walker,
        'reviews': page_obj,  # Используем paginator вместо queryset
        'form': form,
        'user_review': user_review,
        'user_can_review': request.user.is_authenticated and not user_review
    })


@login_required
def become_walker(request):
    if hasattr(request.user, 'walker'):
        messages.warning(request, 'Вы уже отправили заявку ранее!')
        return render(request, 'services/become_walker.html')

    if request.method == 'POST':
        form = WalkerApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            walker = form.save(commit=False)
            walker.user = request.user
            walker.save()
            return redirect('services:walker_thanks')
    else:
        form = WalkerApplicationForm()

    return render(request, 'services/become_walker.html', {'form': form})


def walker_thanks(request):
    return render(request, 'services/walker_thanks.html')


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.author:
        raise PermissionDenied("Вы не можете редактировать этот отзыв")

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            # Пересчитываем рейтинг выгульщика
            walker = review.walker
            walker_rating = Review.objects.filter(
                walker=walker,
                review_type='walker'
            ).aggregate(models.Avg('rating'))['rating__avg']
            walker.rating = round(walker_rating, 1) if walker_rating else 5.0
            walker.save()

            messages.success(request, 'Отзыв успешно обновлён!')
            return redirect('services:walker_detail', walker_id=review.walker.id)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'services/edit_review.html', {
        'form': form,
        'walker': review.walker
    })


# ... остальные представления ...

def privacy_policy(request):
    return render(request, 'legal/privacy_policy.html')


def terms_of_use(request):
    return render(request, 'legal/terms_of_use.html')


def cookie_policy(request):
    return render(request, 'legal/cookie_policy.html')
