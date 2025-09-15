from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_assignments(request):
    """Paginated list of the authenticated paramedic's recent assignments."""
    from emergencies.models import EmergencyCall
    from emergencies.serializers import EmergencyCallSerializer

    if not getattr(request.user, 'is_paramedic', False):
        return Response({'detail': 'Forbidden'}, status=403)

    try:
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
    except ValueError:
        limit, offset = 10, 0

    qs = EmergencyCall.objects.filter(assigned_paramedic=request.user).order_by('-received_at')
    total = qs.count()
    items = qs[offset:offset+limit]
    data = EmergencyCallSerializer(items, many=True).data
    return Response({
        'count': total,
        'next_offset': offset + limit if offset + limit < total else None,
        'results': data,
    })

# Create your views here.
