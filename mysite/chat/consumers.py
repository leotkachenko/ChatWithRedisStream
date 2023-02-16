# chat/consumers.py
import json
from os import environ
from redis import Redis
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        hostname = environ.get("REDIS_HOSTNAME", "localhost")
        port = environ.get("REDIS_PORT", 6379)
        r = Redis(hostname, port, retry_on_timeout=True)
        self.connection = r
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        print(text_data)
        last_id = 0
        sleep_ms = 5000
        resp = self.connection.xread(
            {'oneof': last_id}, count=1, block=sleep_ms
        )
        if resp:
            key, messages = resp[0]
            last_id, data = messages[0]
            print("REDIS ID: ", last_id)
            print("      --> ", data)