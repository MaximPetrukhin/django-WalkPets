from django.urls import path
from .views import login, register, profile, logout, delete_avatar, upload_avatar

app_name = 'users'

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('logout/', logout, name='logout'),
    path('upload-avatar/', upload_avatar, name='upload_avatar'),
    path('delete-avatar/', delete_avatar, name='delete_avatar'),

]