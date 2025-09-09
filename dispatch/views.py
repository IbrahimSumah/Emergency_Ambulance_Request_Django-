from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import render
from .models import Ambulance, Hospital
from .serializers import AmbulanceSerializer, AmbulanceLocationUpdateSerializer, HospitalSerializer, DispatchSerializer


class AmbulanceListView(generics.ListAPIView):
    """API view for listing all ambulances"""
    
    queryset = Ambulance.objects.all()
    serializer_class = AmbulanceSerializer
    permission_classes = [IsAuthenticated]


class AmbulanceDetailView(generics.RetrieveUpdateAPIView):
    """API view for retrieving and updating ambulance details"""
    
    queryset = Ambulance.objects.all()
    serializer_class = AmbulanceSerializer
    permission_classes = [IsAuthenticated]


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
        
        # Send real-time notification
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                'dispatchers',
                {
                    'type': 'ambulance_update',
                    'event': 'LOCATION_UPDATE',
                    'data': AmbulanceSerializer(ambulance).data
                }
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
        emergency_call.update_status('DISPATCHED')
        
        # Send real-time notifications
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        if channel_layer:
            # Notify about unit dispatch
            async_to_sync(channel_layer.group_send)(
                'dispatchers',
                {
                    'type': 'ambulance_update',
                    'event': 'UNIT_DISPATCHED',
                    'data': AmbulanceSerializer(ambulance).data
                }
            )
            
            # Notify about emergency update
            from emergencies.serializers import EmergencyCallSerializer
            async_to_sync(channel_layer.group_send)(
                'dispatchers',
                {
                    'type': 'emergency_update',
                    'event': 'STATUS_UPDATE',
                    'data': EmergencyCallSerializer(emergency_call).data
                }
            )
        
        return Response({
            'message': 'Ambulance dispatched successfully',
            'emergency_call': EmergencyCallSerializer(emergency_call).data,
            'ambulance': AmbulanceSerializer(ambulance).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HospitalListView(generics.ListAPIView):
    """API view for listing all hospitals"""
    
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [IsAuthenticated]


def fleet_overview(request):
    """Fleet overview page"""
    if not request.user.is_authenticated:
        return render(request, 'core/login_required.html')
    
    return render(request, 'dispatch/fleet_overview.html')
