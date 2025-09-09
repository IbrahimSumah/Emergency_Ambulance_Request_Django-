from django.contrib import admin
from .models import DispatcherProfile, ParamedicProfile


@admin.register(DispatcherProfile)
class DispatcherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'experience_years', 'shift_schedule')
    search_fields = ('user__first_name', 'user__last_name', 'employee_id')
    ordering = ('user__last_name',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'employee_id')
        }),
        ('Professional Details', {
            'fields': ('experience_years', 'certifications', 'shift_schedule')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
    )


@admin.register(ParamedicProfile)
class ParamedicProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'license_number', 'license_expiry', 'is_license_valid', 'assigned_ambulance')
    list_filter = ('license_expiry', 'assigned_ambulance')
    search_fields = ('user__first_name', 'user__last_name', 'employee_id', 'license_number')
    ordering = ('user__last_name',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'employee_id')
        }),
        ('License Information', {
            'fields': ('license_number', 'license_expiry')
        }),
        ('Professional Details', {
            'fields': ('experience_years', 'certifications', 'specialties', 'shift_schedule')
        }),
        ('Assignment', {
            'fields': ('assigned_ambulance',)
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
    )
    
    def is_license_valid(self, obj):
        return obj.is_license_valid
    is_license_valid.boolean = True
    is_license_valid.short_description = 'License Valid'
