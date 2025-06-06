from django.shortcuts import render
from services.models import Services

def index(requests):
    return render(requests, "services/index.html")

def services(requests):
    return render(requests, "services/services.html")

def privacy_policy(request):
    return render(request, 'legal/privacy_policy.html')

def terms_of_use(request):
    return render(request, 'legal/terms_of_use.html')

def cookie_policy(request):
    return render(request, 'legal/cookie_policy.html')

def service_list(request):  # Переименовано из services в service_list
    services = Services.objects.filter(is_active=True)  # Добавлено получение услуг
    return render(request, 'services/services.html', {'services': services})