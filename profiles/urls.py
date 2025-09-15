from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    # Add URL patterns here
    path('api/my-assignments/', views.my_assignments, name='my_assignments'),
]
