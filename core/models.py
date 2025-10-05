from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with role-based authentication"""
    ROLE_CHOICES = [
        ('dispatcher', 'Dispatcher'),
        ('paramedic', 'Paramedic'),
        ('admin', 'Administrator'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='dispatcher')
    phone_number = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def is_dispatcher(self):
        return self.role == 'dispatcher'
    
    @property
    def is_paramedic(self):
        return self.role == 'paramedic'

    @property
    def is_admin(self):
        # Treat Django superusers as admins in-app
        return self.role == 'admin' or bool(getattr(self, 'is_superuser', False))

    def save(self, *args, **kwargs):
        # Ensure superusers default to admin role for app-level permissions
        if getattr(self, 'is_superuser', False) and self.role != 'admin':
            self.role = 'admin'
        super().save(*args, **kwargs)