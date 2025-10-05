from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer


def login_view(request):
    """Staff login view"""
    if request.user.is_authenticated:
        if getattr(request.user, 'is_admin', False) or getattr(request.user, 'is_staff', False):
            return redirect('core:admin_dashboard')
        if request.user.is_dispatcher:
            return redirect('emergencies:dispatcher_dashboard')
        elif request.user.is_paramedic:
            return redirect('emergencies:paramedic_interface')
        else:
            return redirect('admin:index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            # Redirect based on user role
            if getattr(user, 'is_admin', False) or getattr(user, 'is_staff', False):
                return redirect('core:admin_dashboard')
            if user.is_dispatcher:
                return redirect('emergencies:dispatcher_dashboard')
            elif user.is_paramedic:
                return redirect('emergencies:paramedic_interface')
            else:
                return redirect('admin:index')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'core/login.html')


@login_required
def logout_view(request):
    """Staff logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('core:login')


def home_view(request):
    """Welcome page or redirect to appropriate dashboard"""
    if request.user.is_authenticated:
        if getattr(request.user, 'is_admin', False) or getattr(request.user, 'is_staff', False):
            return redirect('core:admin_dashboard')
        if request.user.is_dispatcher:
            return redirect('emergencies:dispatcher_dashboard')
        if request.user.is_paramedic:
            return redirect('emergencies:paramedic_interface')
    return render(request, 'core/welcome.html')


@login_required
def admin_dashboard(request):
    if not (getattr(request.user, 'is_admin', False) or getattr(request.user, 'is_staff', False)):
        return render(request, 'core/login_required.html')
    return render(request, 'core/admin_dashboard.html')


# API: Users CRUD (staff/admin only)
User = get_user_model()


class IsStaffOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (getattr(user, 'is_staff', False) or getattr(user, 'is_admin', False)))


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsStaffOrAdmin]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsStaffOrAdmin]

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.id == request.user.id:
            return Response({'error': 'You cannot delete your own account'}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class ParamedicListView(generics.ListAPIView):
    """List active paramedics for dispatcher assignment"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(role='paramedic', is_active=True).order_by('first_name', 'last_name')
