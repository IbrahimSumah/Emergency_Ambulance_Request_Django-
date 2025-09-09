from django.db import models
from django.contrib.auth import get_user_model
from core.models import User


class EmergencyCall(models.Model):
    """Model representing an emergency call from start to finish"""
    
    STATUS_CHOICES = [
        ('RECEIVED', 'Received'),
        ('DISPATCHED', 'Dispatched'),
        ('EN_ROUTE', 'En Route'),
        ('ON_SCENE', 'On Scene'),
        ('TRANSPORTING', 'Transporting'),
        ('AT_HOSPITAL', 'At Hospital'),
        ('CLOSED', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    EMERGENCY_TYPE_CHOICES = [
        ('MEDICAL', 'Medical Emergency'),
        ('TRAUMA', 'Trauma'),
        ('CARDIAC', 'Cardiac Arrest'),
        ('STROKE', 'Stroke'),
        ('RESPIRATORY', 'Respiratory Distress'),
        ('FIRE', 'Fire Emergency'),
        ('OTHER', 'Other'),
    ]
    
    # Basic call information
    call_id = models.CharField(max_length=20, unique=True, blank=True)
    caller_name = models.CharField(max_length=100)
    caller_phone = models.CharField(max_length=15)
    emergency_type = models.CharField(max_length=20, choices=EMERGENCY_TYPE_CHOICES)
    description = models.TextField()
    emergency_images = models.JSONField(default=list, blank=True, help_text="List of image URLs uploaded with the emergency")
    
    # Location information
    location_address = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Status and priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RECEIVED')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    
    # Assignment information
    assigned_ambulance = models.ForeignKey('dispatch.Ambulance', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_paramedic = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_calls')
    dispatcher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='dispatched_calls')
    
    # Timestamps
    received_at = models.DateTimeField(auto_now_add=True)
    dispatched_at = models.DateTimeField(null=True, blank=True)
    en_route_at = models.DateTimeField(null=True, blank=True)
    on_scene_at = models.DateTimeField(null=True, blank=True)
    transporting_at = models.DateTimeField(null=True, blank=True)
    at_hospital_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional information
    patient_name = models.CharField(max_length=100, blank=True)
    patient_age = models.IntegerField(null=True, blank=True)
    patient_condition = models.TextField(blank=True)
    hospital_destination = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-received_at']
        verbose_name = 'Emergency Call'
        verbose_name_plural = 'Emergency Calls'
    
    def __str__(self):
        return f"Call {self.call_id} - {self.emergency_type} ({self.status})"
    
    def save(self, *args, **kwargs):
        if not self.call_id:
            # Generate a unique call ID
            import uuid
            self.call_id = f"CALL-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        return self.status in ['DISPATCHED', 'EN_ROUTE', 'ON_SCENE', 'TRANSPORTING']
    
    @property
    def is_pending(self):
        return self.status == 'RECEIVED'
    
    @property
    def is_completed(self):
        return self.status in ['AT_HOSPITAL', 'CLOSED']
    
    def update_status(self, new_status, user=None):
        """Update status and set appropriate timestamp"""
        from django.utils import timezone
        self.status = new_status
        now = timezone.now()
        
        if new_status == 'DISPATCHED' and not self.dispatched_at:
            self.dispatched_at = now
        elif new_status == 'EN_ROUTE' and not self.en_route_at:
            self.en_route_at = now
        elif new_status == 'ON_SCENE' and not self.on_scene_at:
            self.on_scene_at = now
        elif new_status == 'TRANSPORTING' and not self.transporting_at:
            self.transporting_at = now
        elif new_status == 'AT_HOSPITAL' and not self.at_hospital_at:
            self.at_hospital_at = now
        elif new_status == 'CLOSED' and not self.closed_at:
            self.closed_at = now
            
        self.save()
