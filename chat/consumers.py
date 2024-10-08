import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

# Initialize logger
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'chat_room'
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')

        if message:
            # Send the message to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                }
            )

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message,
        }))
