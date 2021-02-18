from django.urls import re_path
from channels.routing import URLRouter
from django.core.asgi import get_asgi_application

from . import consumers

urlpatterns = URLRouter([
  re_path(r'events/', consumers.ServerSentEventConsumer.as_asgi()),
  re_path(r'^.*$', get_asgi_application())
])