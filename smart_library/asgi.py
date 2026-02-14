"""
ASGI config for smart_library project (Django Channels).
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import library.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_library.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            library.routing.websocket_urlpatterns
        )
    ),
})
