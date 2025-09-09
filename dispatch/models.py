from django.db import models
from django.contrib.auth import get_user_model
from core.models import User


class Ambulance(models.Model):
    """Model representing an ambulance unit in the fleet"""
    
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('EN_ROUTE', 'En Route'),
        ('ON_SCENE', 'On Scene'),
        ('TRANSPORTING', 'Transporting'),
        ('MAINTENANCE', 'Maintenance'),
        ('OUT_OF_SERVICE', 'Out of Service'),
    ]
    
    UNIT_TYPE_CHOICES = [
        ('BASIC', 'Basic Life Support'),
        ('ADVANCED', 'Advanced Life Support'),
        ('CRITICAL', 'Critical Care'),
    ]
    
    # Basic information
    unit_number = models.CharField(max_length=10, unique=True)
    unit_type = models.CharField(max_length=10, choices=UNIT_TYPE_CHOICES, default='BASIC')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    
    # Location information
    current_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # Assignment information
    assigned_paramedic = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_ambulance')
    current_emergency = models.ForeignKey('emergencies.EmergencyCall', on_delete=models.SET_NULL, null=True, blank=True, related_name='ambulance_assignment')
    
    # Equipment and capabilities
    equipment_list = models.TextField(blank=True, help_text="List of equipment available in this unit")
    max_patients = models.IntegerField(default=1)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['unit_number']
        verbose_name = 'Ambulance'
        verbose_name_plural = 'Ambulances'
    
    def __str__(self):
        return f"Unit {self.unit_number} ({self.get_status_display()})"
    
    @property
    def is_available(self):
        return self.status == 'AVAILABLE'
    
    @property
    def is_busy(self):
        return self.status in ['EN_ROUTE', 'ON_SCENE', 'TRANSPORTING']
    
    @property
    def current_location(self):
        if self.current_latitude and self.current_longitude:
            return (float(self.current_latitude), float(self.current_longitude))
        return None
    
    def update_location(self, latitude, longitude):
        """Update the ambulance's current location"""
        self.current_latitude = latitude
        self.current_longitude = longitude
        from django.utils import timezone
        self.last_location_update = timezone.now()
        self.save()
    
    def assign_to_emergency(self, emergency_call, paramedic=None):
        """Assign this ambulance to an emergency call"""
        self.current_emergency = emergency_call
        self.status = 'EN_ROUTE'
        if paramedic:
            self.assigned_paramedic = paramedic
        self.save()
    
    def complete_assignment(self):
        """Mark assignment as complete and return to available status"""
        self.current_emergency = None
        self.status = 'AVAILABLE'
        self.save()


class Hospital(models.Model):
    """Model representing a hospital destination"""
    
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    phone_number = models.CharField(max_length=15, blank=True)
    
    # Capacity information
    total_beds = models.IntegerField(default=0)
    available_beds = models.IntegerField(default=0)
    emergency_capacity = models.CharField(max_length=20, choices=[
        ('LOW', 'Low Load'),
        ('MODERATE', 'Moderate Load'),
        ('HIGH', 'High Load'),
        ('FULL', 'At Capacity'),
    ], default='MODERATE')
    
    # Specialties
    specialties = models.TextField(blank=True, help_text="Comma-separated list of medical specialties")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Hospital'
        verbose_name_plural = 'Hospitals'
    
    def __str__(self):
        return self.name
    
    @property
    def location(self):
        return (float(self.latitude), float(self.longitude))
