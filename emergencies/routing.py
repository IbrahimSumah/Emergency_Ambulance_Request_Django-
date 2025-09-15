from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/dispatchers/$', consumers.DispatcherConsumer.as_asgi()),
    re_path(r'ws/paramedic/$', consumers.ParamedicConsumer.as_asgi()),
]
