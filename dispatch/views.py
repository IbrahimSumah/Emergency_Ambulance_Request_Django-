from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import render
from django.views.decorators.http import require_POST
from .models import Ambulance, Hospital
from .serializers import (
    AmbulanceSerializer,
    AmbulanceLocationUpdateSerializer,
    HospitalSerializer,
    DispatchSerializer,
)
from core.utils import send_ambulance_notification, send_emergency_notification, send_hospital_notification


class AmbulanceListCreateView(generics.ListCreateAPIView):
    """List all ambulances and allow dispatchers to create new units."""

    queryset = Ambulance.objects.all()
    serializer_class = AmbulanceSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not getattr(request.user, "is_dispatcher", False):
            return Response({"error": "Only dispatchers can create ambulances"}, status=status.HTTP_403_FORBIDDEN)

        return super().create(request, *args, **kwargs)


class AmbulanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an ambulance. Delete restricted to dispatchers."""

    queryset = Ambulance.objects.all()
    serializer_class = AmbulanceSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        if not getattr(request.user, "is_dispatcher", False):
            return Response({"error": "Only dispatchers can delete ambulances"}, status=status.HTTP_403_FORBIDDEN)

        ambulance = self.get_object()
        # Prevent deleting units that are currently assigned/busy
        if ambulance.current_emergency_id or not ambulance.is_available:
            return Response({"error": "Cannot delete an ambulance that is assigned or not available"}, status=status.HTTP_400_BAD_REQUEST)

        return super().destroy(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_ambulance_location(request, pk):
    """API endpoint for updating ambulance location"""
    
    try:
        ambulance = Ambulance.objects.get(pk=pk)
    except Ambulance.DoesNotExist:
        return Response({'error': 'Ambulance not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is assigned to this ambulance
    if request.user.is_paramedic and ambulance.assigned_paramedic != request.user:
        return Response({'error': 'Not authorized to update this ambulance'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = AmbulanceLocationUpdateSerializer(ambulance, data=request.data, partial=True)
    
    if serializer.is_valid():
        ambulance = serializer.save()
        
        # Send real-time notification using optimized utility function
        ambulance_data = AmbulanceSerializer(ambulance).data
        send_ambulance_notification(
            event='LOCATION_UPDATE',
            ambulance_data=ambulance_data
        )
        
        return Response(AmbulanceSerializer(ambulance).data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def dispatch_ambulance(request):
    """API endpoint for dispatching an ambulance to an emergency"""
    
    if not request.user.is_dispatcher:
        return Response({'error': 'Only dispatchers can dispatch ambulances'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = DispatchSerializer(data=request.data)
    
    if serializer.is_valid():
        emergency_call_id = serializer.validated_data['emergency_call_id']
        ambulance_id = serializer.validated_data['ambulance_id']
        paramedic_id = serializer.validated_data.get('paramedic_id')
        hospital_id = serializer.validated_data.get('hospital_id')
        
        # Get the objects
        from emergencies.models import EmergencyCall
        emergency_call = EmergencyCall.objects.get(id=emergency_call_id)
        ambulance = Ambulance.objects.get(id=ambulance_id)
        paramedic = None
        
        if paramedic_id:
            from core.models import User
            paramedic = User.objects.get(id=paramedic_id)
        
        # Assign ambulance to emergency
        ambulance.assign_to_emergency(emergency_call, paramedic)
        
        # Update emergency call
        emergency_call.assigned_ambulance = ambulance
        emergency_call.assigned_paramedic = paramedic
        emergency_call.dispatcher = request.user
        if hospital_id:
            from .models import Hospital
            try:
                dest = Hospital.objects.get(id=hospital_id)
                emergency_call.hospital_destination = dest.name
            except Hospital.DoesNotExist:
                pass
        emergency_call.update_status('DISPATCHED')
        
        # Send real-time notifications using optimized utility functions
        from emergencies.serializers import EmergencyCallSerializer
        
        # Notify dispatchers about ambulance dispatch
        ambulance_data = AmbulanceSerializer(ambulance).data
        send_ambulance_notification(
            event='UNIT_DISPATCHED',
            ambulance_data=ambulance_data
        )
        
        # Notify dispatchers about emergency status update
        emergency_data = EmergencyCallSerializer(emergency_call).data
        send_emergency_notification(
            event='STATUS_UPDATE',
            emergency_data=emergency_data,
            paramedic_id=None  # Only send to dispatchers
        )
        
        # Notify assigned paramedic about dispatch (UNIT_DISPATCHED event)
        if emergency_call.assigned_paramedic_id:
            send_emergency_notification(
                event='UNIT_DISPATCHED',
                emergency_data=emergency_data,
                paramedic_id=emergency_call.assigned_paramedic_id
            )
        
        return Response({
            'message': 'Ambulance dispatched successfully',
            'emergency_call': emergency_data,
            'ambulance': ambulance_data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HospitalListCreateView(generics.ListCreateAPIView):
    """List hospitals and allow staff/admin to create new hospitals."""

    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        if not (getattr(user, 'is_staff', False) or getattr(user, 'is_admin', False)):
            return Response({"error": "Only admin/staff can create hospitals"}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
class HospitalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete hospital; restricted to staff/admin for write ops."""

    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user
        # Allow staff/admin full updates; dispatchers limited to safe fields
        if getattr(user, 'is_staff', False) or getattr(user, 'is_admin', False):
            return super().update(request, *args, **kwargs)
        if getattr(user, 'is_dispatcher', False):
            # Whitelist dispatcher-editable fields
            allowed = {
                'name', 'address', 'phone_number', 'specialties',
                'available_beds', 'emergency_capacity', 'total_beds'
            }
            data = {k: v for k, v in request.data.items() if k in allowed}
            if not data:
                return Response({"error": "No permitted fields to update"}, status=status.HTTP_400_BAD_REQUEST)
            partial = True
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        if not (getattr(user, 'is_staff', False) or getattr(user, 'is_admin', False)):
            return Response({"error": "Only admin/staff can delete hospitals"}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


def fleet_overview(request):
    """Fleet overview page"""
    if not request.user.is_authenticated:
        return render(request, 'core/login_required.html')
    
    return render(request, 'dispatch/fleet_overview.html')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_hospital_capacity(request, pk):
    """Allow dispatcher/admin to update hospital capacity and available beds."""
    try:
        hospital = Hospital.objects.get(pk=pk)
    except Hospital.DoesNotExist:
        return Response({'error': 'Hospital not found'}, status=status.HTTP_404_NOT_FOUND)

    # Optional: enforce role permissions here if needed
    allowed_fields = {'available_beds', 'total_beds', 'emergency_capacity'}
    data = {k: v for k, v in request.data.items() if k in allowed_fields}

    serializer = HospitalSerializer(hospital, data=data, partial=True)
    if serializer.is_valid():
        hospital = serializer.save()
        
        # Broadcast update to dispatchers using optimized utility function
        hospital_data = HospitalSerializer(hospital).data
        send_hospital_notification(
            event='CAPACITY_UPDATE',
            hospital_data=hospital_data
        )
        
        return Response(hospital_data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
