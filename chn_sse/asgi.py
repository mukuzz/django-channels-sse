import os

from channels.routing import ProtocolTypeRouter
from . import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chn_sse.settings')

application = ProtocolTypeRouter({
  "http": routing.urlpatterns,
})