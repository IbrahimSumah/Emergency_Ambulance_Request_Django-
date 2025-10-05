from django.urls import path
from . import views

app_name = 'dispatch'

urlpatterns = [
    # Web views
    path('fleet/', views.fleet_overview, name='fleet_overview'),
    
    # API endpoints
    path('api/ambulances/', views.AmbulanceListCreateView.as_view(), name='ambulance_list'),
    path('api/ambulances/<int:pk>/', views.AmbulanceDetailView.as_view(), name='ambulance_detail'),
    path('api/ambulances/<int:pk>/location/', views.update_ambulance_location, name='update_ambulance_location'),
    path('api/hospitals/<int:pk>/capacity/', views.update_hospital_capacity, name='update_hospital_capacity'),
    path('api/dispatch/', views.dispatch_ambulance, name='dispatch_ambulance'),
    path('api/hospitals/', views.HospitalListCreateView.as_view(), name='hospital_list'),
    path('api/hospitals/<int:pk>/', views.HospitalDetailView.as_view(), name='hospital_detail'),
]
