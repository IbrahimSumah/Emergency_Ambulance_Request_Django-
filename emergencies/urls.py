from django.urls import path
from . import views

app_name = 'emergencies'

urlpatterns = [
    # Web views
    path('emergency/', views.landing_page, name='landing'),
    path('staff/dashboard/', views.dispatcher_dashboard, name='dispatcher_dashboard'),
    path('staff/field/', views.paramedic_interface, name='paramedic_interface'),
    
    # API endpoints
    path('api/emergencies/', views.EmergencyCallListCreateView.as_view(), name='emergency_list_create'),
    path('api/emergencies/<int:pk>/', views.EmergencyCallDetailView.as_view(), name='emergency_detail'),
    path('api/emergencies/<int:pk>/status/', views.update_emergency_status, name='update_emergency_status'),
    path('api/emergencies/active/', views.active_emergencies, name='active_emergencies'),
    path('api/emergencies/upload-image/', views.upload_emergency_image, name='upload_emergency_image'),
]
