from django.urls import path
from .views import select_region, wpzona, approve_submission

app_name = 'wpzona'

urlpatterns = [
    path('', select_region, name='select_region'),
    path('region/', wpzona, name='wpzona'),
    path('approve/<int:submission_id>/', approve_submission, name='approve_submission'),
]