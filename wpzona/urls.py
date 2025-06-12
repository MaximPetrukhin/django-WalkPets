from django.urls import path
from .views import wpzona  # Импортируем функцию wpzona

app_name = 'wpzona'

urlpatterns = [
    path('', wpzona, name='wpzona'),
]