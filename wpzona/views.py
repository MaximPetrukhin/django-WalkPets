import requests
from django.conf import settings
from django.shortcuts import render
from .models import PetFriendlyPlace
from .forms import PetFriendlyPlaceForm
from django.shortcuts import render, redirect


def wpzona(request):
    # Получение данных о погоде
    weather_data = None
    API_KEY = settings.OPENWEATHER_API_KEY
    city = "Москва"
    try:
        weather_response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ru"
        )
        weather_data = weather_response.json()
    except requests.RequestException as e:
        print(f"Ошибка при запросе погоды: {e}")

    # Обработка формы
    if request.method == 'POST':
        form = PetFriendlyPlaceForm(request.POST)
        if form.is_valid():
            form.save()
            # Редирект после успешного сохранения чтобы избежать повторной отправки формы
            return redirect('wpzona:wpzona')
    else:
        form = PetFriendlyPlaceForm()

    # Получение мест
    places = PetFriendlyPlace.objects.all().order_by('-created_at')[:10]  # Последние 10 мест

    context = {
        'title': 'WP-zona - Pet-friendly места',
        'weather': weather_data,
        'form': form,
        'places': places,
    }
    return render(request, 'wpzona/wpzona.html', context)