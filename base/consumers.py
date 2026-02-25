import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.apps import apps


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'room_{self.room_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data['message']
        user = self.scope["user"]

        message = await self.save_message(user, message_text)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message.body,
                'username': message.user.username,
                'user_id': message.user.id,
                'message_id': message.id,
                'avatar': message.user.avatar_url,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
            'message_id': event['message_id'],
            'avatar': event['avatar'],
            'current_user_id': self.scope["user"].id,
        }))

    @database_sync_to_async
    def save_message(self, user, message_text):
        Room = apps.get_model('base', 'Room')
        Message = apps.get_model('base', 'Message')

        room = Room.objects.get(id=self.room_id)

        return Message.objects.create(
            user=user,
            room=room,
            body=message_text
        )