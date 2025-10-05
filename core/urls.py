from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # Admin API for users
    path('api/users/', views.UserListCreateView.as_view(), name='user_list_create'),
    path('api/users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    # Utility API
    path('api/paramedics/', views.ParamedicListView.as_view(), name='paramedic_list'),
]
