from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
import requests
from django.contrib import messages
from .models import Region, PetFriendlyPlace, PetFriendlyPlaceSubmission
from .forms import RegionSelectForm, PetFriendlyPlaceSubmissionForm


def select_region(request):
    if request.method == 'POST':
        form = RegionSelectForm(request.POST)
        if form.is_valid():
            region = form.cleaned_data['region']
            request.session['selected_region_id'] = region.id
            return redirect('wpzona:wpzona')
    else:
        form = RegionSelectForm()

    return render(request, 'wpzona/select_region.html', {
        'form': form,
        'title': 'Выбор региона'
    })


def wpzona(request):
    region_id = request.session.get('selected_region_id')
    if not region_id:
        return redirect('wpzona:select_region')

    try:
        region = Region.objects.get(id=region_id)
    except Region.DoesNotExist:
        messages.error(request, 'Выбранный регион не найден')
        return redirect('wpzona:select_region')

    # Weather API call
    weather_data = None
    try:
        weather_response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?"
            f"lat={region.latitude}&lon={region.longitude}"
            f"&appid={settings.OPENWEATHER_API_KEY}"
            f"&units=metric&lang=ru"
        )
        if weather_response.status_code == 200:
            weather_data = weather_response.json()
    except requests.RequestException:
        messages.warning(request, 'Не удалось получить данные о погоде')

    # Handle place submission
    if request.method == 'POST' and request.user.is_authenticated:
        form = PetFriendlyPlaceSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.region = region
            submission.save()
            messages.success(request, 'Ваше предложение отправлено на модерацию!')
            return redirect('wpzona:wpzona')
    else:
        form = PetFriendlyPlaceSubmissionForm()

    # Get approved places
    places = PetFriendlyPlace.objects.filter(submission__region=region).select_related('submission')

    context = {
        'title': f'WPzona - {region.name}',
        'weather': weather_data,
        'form': form,
        'places': places,
        'region': region,
    }
    return render(request, 'wpzona/wpzona.html', context)


@staff_member_required
def approve_submission(request, submission_id):
    try:
        submission = PetFriendlyPlaceSubmission.objects.get(id=submission_id)
        if submission.status != 'approved':
            submission.status = 'approved'
            submission.save()

            # Create approved place
            PetFriendlyPlace.objects.create(
                submission=submission,
                latitude=submission.region.latitude,  # В реальном приложении нужно получать координаты адреса
                longitude=submission.region.longitude
            )
            messages.success(request, 'Место успешно одобрено!')
        else:
            messages.info(request, 'Это место уже было одобрено ранее')
    except PetFriendlyPlaceSubmission.DoesNotExist:
        messages.error(request, 'Заявка не найдена')

    return redirect('admin:wpzona_petfriendlyplacesubmission_changelist')