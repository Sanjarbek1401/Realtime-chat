import json
import logging
import os
# import requests
from channels.generic.websocket import AsyncWebsocketConsumer
from dotenv import load_dotenv
import openai

# Initialize logger
logger = logging.getLogger(__name__)

# Environment variables'ni yuklash
load_dotenv()

class AIConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'ai_room'
        self.room_group_name = 'ai_group'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        user_message = data.get('message')

        if not user_message:
            await self.send(text_data=json.dumps({
                'error': "No message received. Please provide input."
            }))
            return

        # Call SambaNova API to get AI response
        try:
            # Initialize OpenAI client with API key
            client = openai.OpenAI(
                api_key=os.getenv("SAMBANOVA_API_KEY"),
                base_url="https://api.sambanova.ai/v1/",
            )

            # Create a chat completion request
            response = client.chat.completions.create(
                model='Meta-Llama-3.1-8B-Instruct',
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                top_p=0.1
            )
            print(response.choices[0].message.content)

            ai_response = response.choices[0].message.content

            # Send the response back to the frontend
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'ai_message',
                    'user_message': user_message,
                    'ai_response': ai_response,
                }
            )

        except Exception as e:
            logger.error(f"Error connecting to SambaNova API: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': "Failed to connect to SambaNova API. Please try again later."
            }))

    async def ai_message(self, event):
        user_message = event['user_message']
        ai_response = event['ai_response']

        await self.send(text_data=json.dumps({
            'user_message': user_message,
            'ai_response': ai_response,
        }))
