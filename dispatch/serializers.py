from rest_framework import serializers
from .models import Ambulance, Hospital
from core.models import User


class AmbulanceSerializer(serializers.ModelSerializer):
    """Serializer for Ambulance model"""
    
    assigned_paramedic_name = serializers.CharField(source='assigned_paramedic.get_full_name', read_only=True)
    current_emergency_id = serializers.CharField(source='current_emergency.call_id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    unit_type_display = serializers.CharField(source='get_unit_type_display', read_only=True)
    
    class Meta:
        model = Ambulance
        fields = [
            'id', 'unit_number', 'unit_type', 'unit_type_display', 'status', 'status_display',
            'current_latitude', 'current_longitude', 'last_location_update',
            'assigned_paramedic', 'assigned_paramedic_name', 'current_emergency',
            'current_emergency_id', 'equipment_list', 'max_patients',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_location_update']


class AmbulanceLocationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating ambulance location"""
    
    class Meta:
        model = Ambulance
        fields = ['current_latitude', 'current_longitude']
    
    def validate(self, data):
        """Validate location coordinates"""
        lat = data.get('current_latitude')
        lng = data.get('current_longitude')
        
        if lat is not None and (lat < -90 or lat > 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        
        if lng is not None and (lng < -180 or lng > 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        
        return data


class HospitalSerializer(serializers.ModelSerializer):
    """Serializer for Hospital model"""
    
    emergency_capacity_display = serializers.CharField(source='get_emergency_capacity_display', read_only=True)
    
    class Meta:
        model = Hospital
        fields = [
            'id', 'name', 'address', 'latitude', 'longitude', 'phone_number',
            'total_beds', 'available_beds', 'emergency_capacity', 'emergency_capacity_display',
            'specialties', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DispatchSerializer(serializers.Serializer):
    """Serializer for dispatch operations"""
    
    emergency_call_id = serializers.IntegerField()
    ambulance_id = serializers.IntegerField()
    paramedic_id = serializers.IntegerField(required=False)
    hospital_id = serializers.IntegerField(required=False)
    
    def validate_emergency_call_id(self, value):
        """Validate emergency call exists and is in correct status"""
        from emergencies.models import EmergencyCall
        try:
            emergency_call = EmergencyCall.objects.get(id=value)
            if emergency_call.status != 'RECEIVED':
                raise serializers.ValidationError("Emergency call must be in RECEIVED status to dispatch")
            return value
        except EmergencyCall.DoesNotExist:
            raise serializers.ValidationError("Emergency call not found")
    
    def validate_ambulance_id(self, value):
        """Validate ambulance exists and is available"""
        try:
            ambulance = Ambulance.objects.get(id=value)
            if not ambulance.is_available:
                raise serializers.ValidationError("Ambulance is not available for dispatch")
            return value
        except Ambulance.DoesNotExist:
            raise serializers.ValidationError("Ambulance not found")
    
    def validate_paramedic_id(self, value):
        """Validate paramedic exists and is a paramedic"""
        if value:
            try:
                paramedic = User.objects.get(id=value)
                if not paramedic.is_paramedic:
                    raise serializers.ValidationError("User is not a paramedic")
                return value
            except User.DoesNotExist:
                raise serializers.ValidationError("Paramedic not found")
        return value

    def validate_hospital_id(self, value):
        if value:
            from .models import Hospital
            try:
                Hospital.objects.get(id=value)
                return value
            except Hospital.DoesNotExist:
                raise serializers.ValidationError("Hospital not found")
        return value
