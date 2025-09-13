import re
from rest_framework import serializers
from .models import EmergencyCall
from dispatch.models import Ambulance
from core.models import User


class EmergencyCallSerializer(serializers.ModelSerializer):
    """Serializer for EmergencyCall model"""
    
    assigned_ambulance_unit = serializers.CharField(source='assigned_ambulance.unit_number', read_only=True)
    assigned_paramedic_name = serializers.CharField(source='assigned_paramedic.get_full_name', read_only=True)
    dispatcher_name = serializers.CharField(source='dispatcher.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    emergency_type_display = serializers.CharField(source='get_emergency_type_display', read_only=True)
    
    class Meta:
        model = EmergencyCall
        fields = [
            'id', 'call_id', 'caller_name', 'caller_phone', 'emergency_type', 'emergency_type_display',
            'description', 'location_address', 'latitude', 'longitude', 'status', 'status_display',
            'priority', 'priority_display', 'assigned_ambulance', 'assigned_ambulance_unit',
            'assigned_paramedic', 'assigned_paramedic_name', 'dispatcher', 'dispatcher_name',
            'patient_name', 'patient_age', 'patient_condition', 'hospital_destination',
            'received_at', 'dispatched_at', 'en_route_at', 'on_scene_at', 'transporting_at',
            'at_hospital_at', 'closed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['call_id', 'received_at', 'created_at', 'updated_at']


class EmergencyCallCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new emergency calls (public API)"""
    
    class Meta:
        model = EmergencyCall
        fields = [
            'caller_name', 'caller_phone', 'emergency_type', 'description',
            'location_address', 'latitude', 'longitude', 'emergency_images'
        ]
    
    def validate(self, data):
        # Ensure required fields are present
        required_fields = ['caller_name', 'caller_phone', 'emergency_type', 'description', 'location_address']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(f"{field} is required")
        
        # Validate phone number format
        phone = data.get('caller_phone', '')
        # Accept both +232XXXXXXXX and XXXXXXXXX formats
        if not re.match(r'^(\+232|0)?[0-9]{8,9}$', phone):
            raise serializers.ValidationError("Phone number must be in format +232XXXXXXXX or 0XXXXXXXX")
        
        # Validate and round coordinates if provided
        if 'latitude' in data and data['latitude'] is not None:
            lat = float(data['latitude'])
            if lat < -90 or lat > 90:
                raise serializers.ValidationError("Latitude must be between -90 and 90 degrees")
            data['latitude'] = round(lat, 6)
        
        if 'longitude' in data and data['longitude'] is not None:
            lng = float(data['longitude'])
            if lng < -180 or lng > 180:
                raise serializers.ValidationError("Longitude must be between -180 and 180 degrees")
            data['longitude'] = round(lng, 6)
        
        return data


class EmergencyCallStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating emergency call status (paramedic API)"""
    
    class Meta:
        model = EmergencyCall
        fields = ['status', 'patient_condition', 'hospital_destination']
    
    def validate_status(self, value):
        """Validate status transitions"""
        if self.instance:
            current_status = self.instance.status
            valid_transitions = {
                'RECEIVED': ['DISPATCHED'],
                'DISPATCHED': ['EN_ROUTE'],
                'EN_ROUTE': ['ON_SCENE'],
                'ON_SCENE': ['TRANSPORTING'],
                'TRANSPORTING': ['AT_HOSPITAL'],
                'AT_HOSPITAL': ['CLOSED'],
            }
            
            if value not in valid_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot transition from {current_status} to {value}"
                )
        return value
