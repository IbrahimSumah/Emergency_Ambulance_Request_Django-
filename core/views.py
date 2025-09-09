from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect


def login_view(request):
    """Staff login view"""
    if request.user.is_authenticated:
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
    """Welcome page - shows options for different user types"""
    return render(request, 'core/welcome.html')
