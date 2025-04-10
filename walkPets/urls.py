"""
URL configuration for walkPets project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from services.views import index
from services.views import services
from services.views import privacy_policy
from services.views import terms_of_use
from services.views import cookie_policy

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name="index"),
    path('services/', services, name="services"),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('terms-of-use/', terms_of_use, name='terms_of_use'),
    path('cookie-policy/', cookie_policy, name='cookie_policy'),
]
