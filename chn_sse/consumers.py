from channels.generic.http import AsyncHttpConsumer
from channels.exceptions import StopConsumer
from datetime import datetime

class AsyncHttpSseConsumer(AsyncHttpConsumer):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.keep_alive = False

  async def send_body(self, body, *, more_body=False):
    """
    Sends a response body to the client. The method expects a bytestring.

    Set ``more_body=True`` if you want to send more body content later.
    The default behavior closes the response, and further messages on
    the channel will be ignored.
    """
    if more_body:
      self.keep_alive = True
    assert isinstance(body, bytes), "Body is not bytes"
    await self.send(
      {"type": "http.response.body", "body": body, "more_body": more_body}
    )

  async def http_request(self, message):
    """
    Async entrypoint - concatenates body fragments and hands off control
    to ``self.handle`` when the body has been completely received.
    """
    if "body" in message:
      self.body.append(message["body"])
    if not message.get("more_body"):
      try:
        await self.handle(b"".join(self.body))
      finally:
        if not self.keep_alive:
          await self.disconnect()
          raise StopConsumer()

class ServerSentEventConsumer(AsyncHttpSseConsumer):

  async def handle(self, body):
    self.room_group_name = 'my_channel'
    await self.channel_layer.group_add(
      self.room_group_name,
      self.channel_name
    )
    await self.send_headers(headers=[
      (b"Cache-Control", b"no-cache"),
      (b"Content-Type", b"text/event-stream"),
      # (b"Transfer-Encoding", b"chunked")
    ])
    # The ASGI spec requires that the protocol server only starts
    # sending the response to the client after ``self.send_body`` has been
    # called the first time.
    await self.send_body("".encode("utf-8"), more_body=True)

  async def disconnect(self):
    await self.channel_layer.group_discard(
      self.room_group_name,
      self.channel_name
    )
  
  async def send_update(self, event):
    payload = "data: %s\n\n" % event['data']
    await self.send_body(payload.encode("utf-8"), more_body=True)