from django.db import models
from django.contrib.auth import get_user_model
from core.models import User


class DispatcherProfile(models.Model):
    """Extended profile for dispatchers"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dispatcher_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    shift_schedule = models.CharField(max_length=100, blank=True)
    certifications = models.TextField(blank=True, help_text="List of relevant certifications")
    experience_years = models.IntegerField(default=0)
    
    # Contact information
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Dispatcher Profile'
        verbose_name_plural = 'Dispatcher Profiles'
    
    def __str__(self):
        return f"Dispatcher {self.user.get_full_name()}"


class ParamedicProfile(models.Model):
    """Extended profile for paramedics"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='paramedic_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField(null=True, blank=True)
    
    # Medical qualifications
    certifications = models.TextField(blank=True, help_text="List of medical certifications")
    specialties = models.TextField(blank=True, help_text="Medical specialties")
    experience_years = models.IntegerField(default=0)
    
    # Assignment information
    assigned_ambulance = models.ForeignKey('dispatch.Ambulance', on_delete=models.SET_NULL, null=True, blank=True)
    shift_schedule = models.CharField(max_length=100, blank=True)
    
    # Contact information
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Paramedic Profile'
        verbose_name_plural = 'Paramedic Profiles'
    
    def __str__(self):
        return f"Paramedic {self.user.get_full_name()}"
    
    @property
    def is_license_valid(self):
        if not self.license_expiry:
            return False
        from django.utils import timezone
        return self.license_expiry > timezone.now().date()
