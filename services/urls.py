from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='services'),  # Главная страница услуг
    path('categories/', views.category_list, name='category_list'),
    path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
    path('all/', views.service_list, name='service_list'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_of_use, name='terms_of_use'),
    path('cookies/', views.cookie_policy, name='cookie_policy'),
    path('become-walker/', views.become_walker, name='become_walker'),
    path('walker-thanks/', views.walker_thanks, name='walker_thanks'),
    path('service/<int:service_id>/', views.service_detail, name='service_detail'),
    path('walkers/', views.walker_list, name='walker_list'),
    path('walkers/<int:walker_id>/', views.walker_detail, name='walker_detail'),

]
