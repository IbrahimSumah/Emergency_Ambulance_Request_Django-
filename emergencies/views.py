from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
import os
import uuid
from .models import EmergencyCall
from .serializers import EmergencyCallSerializer, EmergencyCallCreateSerializer, EmergencyCallStatusUpdateSerializer


class EmergencyCallListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating emergency calls"""
    
    queryset = EmergencyCall.objects.all()
    permission_classes = [AllowAny]  # Public API for emergency calls
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmergencyCallCreateSerializer
        return EmergencyCallSerializer
    
    def create(self, request, *args, **kwargs):
        """Handle emergency call creation with optional image uploads"""
        # Handle JSON data
        if request.content_type == 'application/json':
            data = request.data.copy()
            
            # Process any base64 encoded images if present
            if 'emergency_images' in data and isinstance(data['emergency_images'], list):
                # Convert base64 images to files and upload them
                processed_images = []
                for img_data in data['emergency_images']:
                    if isinstance(img_data, str) and img_data.startswith('data:image'):
                        # This is a base64 encoded image
                        try:
                            from django.core.files.base import ContentFile
                            import base64
                            import uuid
                            # Extract the base64 data
                            format, imgstr = img_data.split(';base64,')
                            ext = format.split('/')[-1]
                            # Create a file-like object
                            file_content = ContentFile(
                                base64.b64decode(imgstr),
                                name=f"emergency_img_{uuid.uuid4()}.{ext}"
                            )
                            # Save the file temporarily
                            processed_images.append(file_content)
                        except Exception as e:
                            logger.error(f"Error processing base64 image: {str(e)}")
                            continue
                
                # Replace base64 data with placeholder URLs that will be updated after save
                data['emergency_images'] = [{'url': f'temp_{i}'} for i in range(len(processed_images))]
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer, processed_images)
            
        # Handle form data (for direct file uploads)
        elif 'multipart/form-data' in request.content_type:
            data = request.data.copy()
            files = request.FILES.getlist('images', [])
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            emergency_call = serializer.save()
            
            # Process uploaded files
            for file in files:
                emergency_call.add_emergency_image(file)
                
            # Send notification after all files are processed
            self.send_notification('NEW_EMERGENCY', emergency_call)
            
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
        else:
            return Response(
                {'error': 'Unsupported content type'}, 
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            )
    
    def perform_create(self, serializer, uploaded_files=None):
        """Create a new emergency call and handle file uploads"""
        emergency_call = serializer.save()
        
        # Process any uploaded files
        if uploaded_files:
            for file in uploaded_files:
                emergency_call.add_emergency_image(file)
        
        # Send real-time notification
        self.send_notification('NEW_EMERGENCY', emergency_call)
    
    def send_notification(self, event_type, emergency_call):
        """Send WebSocket notification"""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            import json
            
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    'dispatchers',
                    {
                        'type': 'emergency_update',
                        'event': event_type,
                        'data': EmergencyCallSerializer(emergency_call).data
                    }
                )
        except Exception as e:
            # Log the error but don't fail the request
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send WebSocket notification: {e}")


class EmergencyCallDetailView(generics.RetrieveUpdateAPIView):
    """API view for retrieving and updating emergency calls"""
    
    queryset = EmergencyCall.objects.all()
    serializer_class = EmergencyCallSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_update(self, serializer):
        """Update emergency call and send notification"""
        old_status = self.get_object().status
        emergency_call = serializer.save()
        
        if old_status != emergency_call.status:
            self.send_notification('STATUS_UPDATE', emergency_call)
    
    def send_notification(self, event_type, emergency_call):
        """Send WebSocket notification"""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    'dispatchers',
                    {
                        'type': 'emergency_update',
                        'event': event_type,
                        'data': EmergencyCallSerializer(emergency_call).data
                    }
                )
        except Exception as e:
            # Log the error but don't fail the request
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send WebSocket notification: {e}")


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_emergency_status(request, pk):
    """API endpoint for paramedics to update emergency call status"""
    
    try:
        emergency_call = EmergencyCall.objects.get(pk=pk)
    except EmergencyCall.DoesNotExist:
        return Response({'error': 'Emergency call not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is assigned to this call
    if request.user.is_paramedic and emergency_call.assigned_paramedic != request.user:
        return Response({'error': 'Not authorized to update this call'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = EmergencyCallStatusUpdateSerializer(emergency_call, data=request.data, partial=True)
    
    if serializer.is_valid():
        old_status = emergency_call.status
        emergency_call = serializer.save()
        
        # Send real-time notification
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    'dispatchers',
                    {
                        'type': 'emergency_update',
                        'event': 'STATUS_UPDATE',
                        'data': EmergencyCallSerializer(emergency_call).data
                    }
                )
        except Exception as e:
            # Log the error but don't fail the request
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send WebSocket notification: {e}")
        
        return Response(EmergencyCallSerializer(emergency_call).data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_emergencies(request):
    """API endpoint for getting active emergency calls"""
    
    status_filter = request.GET.get('status', 'active')
    
    if status_filter == 'active':
        queryset = EmergencyCall.objects.filter(status__in=['DISPATCHED', 'EN_ROUTE', 'ON_SCENE', 'TRANSPORTING'])
    elif status_filter == 'pending':
        queryset = EmergencyCall.objects.filter(status='RECEIVED')
    elif status_filter == 'completed':
        queryset = EmergencyCall.objects.filter(status__in=['AT_HOSPITAL', 'CLOSED'])
    else:
        queryset = EmergencyCall.objects.all()
    
    serializer = EmergencyCallSerializer(queryset, many=True)
    return Response(serializer.data)


def landing_page(request):
    """Landing page for emergency call requests"""
    return render(request, 'emergencies/landing.html')


def dispatcher_dashboard(request):
    """Dispatcher dashboard view"""
    if not request.user.is_authenticated or not request.user.is_dispatcher:
        return render(request, 'core/login_required.html')
    
    return render(request, 'emergencies/dispatcher_dashboard.html')


def paramedic_interface(request):
    """Paramedic field interface"""
    if not request.user.is_authenticated or not request.user.is_paramedic:
        return render(request, 'core/login_required.html')
    
    # Get the paramedic's active call
    active_call = EmergencyCall.objects.filter(
        assigned_paramedic=request.user,
        status__in=['DISPATCHED', 'EN_ROUTE', 'ON_SCENE', 'TRANSPORTING']
    ).first()
    
    context = {
        'active_call': active_call
    }
    
    return render(request, 'emergencies/paramedic_interface.html', context)


@api_view(['POST'])
@permission_classes([AllowAny])
def upload_emergency_image(request):
    """API endpoint for uploading emergency images"""
    if 'image' not in request.FILES:
        return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    image_file = request.FILES['image']
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if image_file.content_type not in allowed_types:
        return Response({'error': 'Invalid file type. Only JPEG, PNG, GIF, and WebP images are allowed.'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file size (max 5MB)
    if image_file.size > 5 * 1024 * 1024:
        return Response({'error': 'File too large. Maximum size is 5MB.'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Generate unique filename
        file_extension = os.path.splitext(image_file.name)[1]
        unique_filename = f"emergency_images/{uuid.uuid4()}{file_extension}"
        
        # Save file
        file_path = default_storage.save(unique_filename, image_file)
        file_url = default_storage.url(file_path)
        
        return Response({
            'success': True,
            'image_url': file_url,
            'filename': unique_filename
        })
        
    except Exception as e:
        return Response({'error': f'Failed to upload image: {str(e)}'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)
