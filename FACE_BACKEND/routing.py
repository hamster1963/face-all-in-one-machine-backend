from channels.routing import ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import face_machine_client.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': (
        URLRouter(
            face_machine_client.routing.websocket_urlpatterns
        )
    ),
})
