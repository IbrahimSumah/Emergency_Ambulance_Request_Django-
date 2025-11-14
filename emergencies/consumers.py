import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class DispatcherConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for dispatcher dashboard real-time updates"""
    
    async def connect(self):
        """Connect to dispatcher group"""
        user = self.scope.get("user", AnonymousUser())
        
        # Log connection attempt for debugging
        logger.info(f"WebSocket connection attempt - User: {user}, Is Authenticated: {user != AnonymousUser()}, Is Dispatcher: {getattr(user, 'is_dispatcher', False)}")
        
        # Check if user is authenticated and is a dispatcher
        if user == AnonymousUser() or not getattr(user, 'is_dispatcher', False):
            logger.warning(f"WebSocket connection rejected - User: {user}, Is Authenticated: {user != AnonymousUser()}, Is Dispatcher: {getattr(user, 'is_dispatcher', False)}")
            await self.close(code=4001)  # Custom close code for unauthorized
            return
        
        self.group_name = 'dispatchers'
        
        # Join dispatcher group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial data
        await self.send_initial_data()
    
    async def disconnect(self, close_code):
        """Leave dispatcher group"""
        logger.info(f"WebSocket disconnecting - Close code: {close_code}")
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
            elif message_type == 'get_initial_data':
                await self.send_initial_data()
                
        except json.JSONDecodeError:
            pass
    
    async def emergency_update(self, event):
        """Handle emergency call updates"""
        await self.send(text_data=json.dumps({
            'type': 'emergency_update',
            'event': event['event'],
            'data': event['data']
        }))
    
    async def ambulance_update(self, event):
        """Handle ambulance updates"""
        await self.send(text_data=json.dumps({
            'type': 'ambulance_update',
            'event': event['event'],
            'data': event['data']
        }))
    
    async def send_initial_data(self):
        """Send initial data to the dispatcher"""
        try:
            # Get active emergencies
            emergencies = await self.get_active_emergencies()
            
            # Get ambulance fleet
            ambulances = await self.get_ambulance_fleet()
            
            # Get hospitals
            hospitals = await self.get_hospitals()
            
            await self.send(text_data=json.dumps({
                'type': 'initial_data',
                'data': {
                    'emergencies': emergencies,
                    'ambulances': ambulances,
                    'hospitals': hospitals
                }
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    @database_sync_to_async
    def get_active_emergencies(self):
        """Get active emergency calls"""
        from .models import EmergencyCall
        from .serializers import EmergencyCallSerializer
        
        emergencies = EmergencyCall.objects.filter(
            status__in=['RECEIVED', 'DISPATCHED', 'EN_ROUTE', 'ON_SCENE', 'TRANSPORTING']
        ).order_by('-received_at')
        
        return EmergencyCallSerializer(emergencies, many=True).data
    
    @database_sync_to_async
    def get_ambulance_fleet(self):
        """Get ambulance fleet data"""
        from dispatch.models import Ambulance
        from dispatch.serializers import AmbulanceSerializer
        
        ambulances = Ambulance.objects.all()
        return AmbulanceSerializer(ambulances, many=True).data
    
    @database_sync_to_async
    def get_hospitals(self):
        """Get hospital data"""
        from dispatch.models import Hospital
        from dispatch.serializers import HospitalSerializer
        
        hospitals = Hospital.objects.all()
        return HospitalSerializer(hospitals, many=True).data


class ParamedicConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for paramedic field interface updates"""
    async def connect(self):
        user = self.scope.get("user", AnonymousUser())
        
        # Log connection attempt for debugging
        logger.info(f"Paramedic WebSocket connection attempt - User: {user}, Is Authenticated: {user != AnonymousUser()}, Is Paramedic: {getattr(user, 'is_paramedic', False)}")
        
        if user == AnonymousUser() or not getattr(user, 'is_paramedic', False):
            logger.warning(f"Paramedic WebSocket connection rejected - User: {user}, Is Authenticated: {user != AnonymousUser()}, Is Paramedic: {getattr(user, 'is_paramedic', False)}")
            await self.close(code=4001)  # Custom close code for unauthorized
            return
        self.group_name = f"paramedic_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        logger.info(f"Paramedic WebSocket disconnecting - Close code: {close_code}")
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Paramedic client can ping to keepalive
        try:
            data = json.loads(text_data)
            if data.get('type') == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
        except Exception:
            pass

    async def emergency_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'emergency_update',
            'event': event['event'],
            'data': event['data']
        }))