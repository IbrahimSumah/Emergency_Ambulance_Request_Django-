from django.contrib import admin
from .models import EmergencyCall


@admin.register(EmergencyCall)
class EmergencyCallAdmin(admin.ModelAdmin):
    list_display = ('call_id', 'emergency_type', 'status', 'priority', 'location_address', 'received_at', 'assigned_ambulance')
    list_filter = ('status', 'priority', 'emergency_type', 'received_at')
    search_fields = ('call_id', 'caller_name', 'caller_phone', 'location_address')
    readonly_fields = ('call_id', 'received_at', 'created_at', 'updated_at')
    ordering = ('-received_at',)
    
    fieldsets = (
        ('Call Information', {
            'fields': ('call_id', 'caller_name', 'caller_phone', 'emergency_type', 'description', 'priority')
        }),
        ('Location', {
            'fields': ('location_address', 'latitude', 'longitude')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'assigned_ambulance', 'assigned_paramedic', 'dispatcher')
        }),
        ('Patient Information', {
            'fields': ('patient_name', 'patient_age', 'patient_condition', 'hospital_destination')
        }),
        ('Timestamps', {
            'fields': ('received_at', 'dispatched_at', 'en_route_at', 'on_scene_at', 'transporting_at', 'at_hospital_at', 'closed_at'),
            'classes': ('collapse',)
        }),
    )
