from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
import requests
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

    return render(request, 'wpzona/select_region.html', {'form': form})


def wpzona(request):
    # Проверяем, выбран ли регион
    region_id = request.session.get('selected_region_id')
    if not region_id:
        return redirect('wpzona:select_region')

    try:
        region = Region.objects.get(id=region_id)
    except Region.DoesNotExist:
        return redirect('wpzona:select_region')

    # Получаем погоду для региона
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
    except requests.RequestException as e:
        print(f"Ошибка при запросе погоды: {e}")

    # Обработка формы добавления места
    if request.method == 'POST' and request.user.is_authenticated:
        form = PetFriendlyPlaceSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.region = region
            submission.save()
            return redirect('wpzona:wpzona')
    else:
        form = PetFriendlyPlaceSubmissionForm()

    # Получаем одобренные места для региона
    places = PetFriendlyPlace.objects.filter(submission__region=region)

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
    # Здесь должна быть логика одобрения заявки
    pass