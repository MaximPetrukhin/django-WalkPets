from django.urls import path
from .views import login, register, profile, logout, create_review, reviews_list, delete_review

app_name = 'users'

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('logout/', logout, name='logout'),
    path('reviews/', reviews_list, name='reviews'),
    path('reviews/create/', create_review, name='create_review'),
    path('reviews/delete/<int:review_id>/', delete_review, name='delete_review'),
]