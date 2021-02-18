from django.shortcuts import render, HttpResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime

def index(request):
  return render(request, 'chn_sse/index.html', {})

def update(request):
  layer = get_channel_layer()
  res = async_to_sync(layer.group_send)(
    "my_channel",
    {
      "type": "send.update",
      "data": [[i*1, i*2, i*3] for i in range(100000)],
    }
  )
  return HttpResponse()