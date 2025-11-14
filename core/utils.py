"""
Utility functions for channel layer notifications and async operations.
Optimized for ASGI applications.
"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def send_channel_notification(
    group_name: str,
    message_type: str,
    event: str,
    data: Dict[str, Any],
    paramedic_id: Optional[int] = None
) -> None:
    """
    Send a notification to a channel group (optimized for ASGI).
    
    This function handles channel layer notifications from sync views.
    It uses async_to_sync to bridge sync/async boundaries.
    
    Args:
        group_name: The channel group name (e.g., 'dispatchers')
        message_type: The message type for the consumer handler (e.g., 'emergency_update')
        event: The event type (e.g., 'NEW_EMERGENCY', 'STATUS_UPDATE')
        data: The data payload to send
        paramedic_id: Optional paramedic ID to also notify their personal channel
    """
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        if not channel_layer:
            logger.warning("Channel layer not configured. Notification not sent.")
            return
        
        # Send notification to the main group
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': message_type,
                'event': event,
                'data': data
            }
        )
        
        # Also notify paramedic's personal channel if provided
        if paramedic_id is not None:
            async_to_sync(channel_layer.group_send)(
                f'paramedic_{paramedic_id}',
                {
                    'type': message_type,
                    'event': event,
                    'data': data
                }
            )
            
    except Exception as e:
        # Log the error but don't fail the request
        logger.warning(f"Failed to send channel notification to {group_name}: {e}", exc_info=True)


def send_emergency_notification(
    event: str,
    emergency_data: Dict[str, Any],
    paramedic_id: Optional[int] = None
) -> None:
    """
    Send an emergency-related notification to dispatchers and optionally to a paramedic.
    
    Args:
        event: The event type (e.g., 'NEW_EMERGENCY', 'STATUS_UPDATE')
        emergency_data: Serialized emergency call data
        paramedic_id: Optional paramedic ID to also notify
    """
    send_channel_notification(
        group_name='dispatchers',
        message_type='emergency_update',
        event=event,
        data=emergency_data,
        paramedic_id=paramedic_id
    )


def send_ambulance_notification(
    event: str,
    ambulance_data: Dict[str, Any]
) -> None:
    """
    Send an ambulance-related notification to dispatchers.
    
    Args:
        event: The event type (e.g., 'LOCATION_UPDATE', 'UNIT_DISPATCHED')
        ambulance_data: Serialized ambulance data
    """
    send_channel_notification(
        group_name='dispatchers',
        message_type='ambulance_update',
        event=event,
        data=ambulance_data
    )


def send_hospital_notification(
    event: str,
    hospital_data: Dict[str, Any]
) -> None:
    """
    Send a hospital-related notification to dispatchers.
    
    Args:
        event: The event type (e.g., 'CAPACITY_UPDATE')
        hospital_data: Serialized hospital data
    """
    send_channel_notification(
        group_name='dispatchers',
        message_type='hospital_update',
        event=event,
        data=hospital_data
    )

