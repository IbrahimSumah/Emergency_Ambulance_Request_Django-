from django.contrib import admin
from .models import Ambulance, Hospital


@admin.register(Ambulance)
class AmbulanceAdmin(admin.ModelAdmin):
    list_display = ('unit_number', 'unit_type', 'status', 'assigned_paramedic', 'current_emergency', 'last_location_update')
    list_filter = ('status', 'unit_type', 'last_location_update')
    search_fields = ('unit_number', 'assigned_paramedic__first_name', 'assigned_paramedic__last_name')
    readonly_fields = ('created_at', 'updated_at', 'last_location_update')
    ordering = ('unit_number',)
    
    fieldsets = (
        ('Unit Information', {
            'fields': ('unit_number', 'unit_type', 'status', 'equipment_list', 'max_patients')
        }),
        ('Location', {
            'fields': ('current_latitude', 'current_longitude', 'last_location_update')
        }),
        ('Assignment', {
            'fields': ('assigned_paramedic', 'current_emergency')
        }),
    )


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'emergency_capacity', 'available_beds', 'total_beds')
    list_filter = ('emergency_capacity',)
    search_fields = ('name', 'address', 'specialties')
    ordering = ('name',)
    
    fieldsets = (
        ('Hospital Information', {
            'fields': ('name', 'address', 'phone_number', 'specialties')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Capacity', {
            'fields': ('total_beds', 'available_beds', 'emergency_capacity')
        }),
    )
