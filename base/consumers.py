import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.apps import apps
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'room_{self.room_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Send current participants list to the newly connected user
        await self.send_participants_update()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Optionally, you could send an update when someone disconnects
        # but since we track participants by messages, we don't need to remove them

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope["user"]
        
        # Handle different message types
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            message_text = data['message']
            message = await self.save_message(user, message_text)
            
            # Send the new message to everyone
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
            
            # Send updated participants list to everyone
            await self.send_participants_update()

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',  # Add type to distinguish in frontend
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
            'message_id': event['message_id'],
            'avatar': event['avatar'],
            'current_user_id': self.scope["user"].id,
        }))

    async def send_participants_update(self):
        """Send updated participants list to all users in the room"""
        participants_data = await self.get_room_participants()
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'participants_update',
                'participants': participants_data['participants'],
                'count': participants_data['count']
            }
        )

    async def participants_update(self, event):
        """Send participants update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'participants_update',
            'participants': event['participants'],
            'count': event['count']
        }))

    @database_sync_to_async
    def get_room_participants(self):
        """Get all participants who have sent messages in this room"""
        Room = apps.get_model('base', 'Room')
        Message = apps.get_model('base', 'Message')
        
        room = Room.objects.get(id=self.room_id)
        
        # Get unique users who have sent messages in this room
        # Include the room host as well
        message_users = Message.objects.filter(room=room).values_list('user', flat=True).distinct()
        
        # Get all participants (message senders + host)
        user_ids = set(message_users)
        user_ids.add(room.host.id)  # Always include the host
        
        users = User.objects.filter(id__in=user_ids)
        
        participants_list = []
        for user in users:
            participants_list.append({
                'id': user.id,
                'username': user.username,
                'avatar': user.avatar_url if hasattr(user, 'avatar_url') else '/static/images/avatar.svg',
            })
        
        return {
            'participants': participants_list,
            'count': len(participants_list)
        }

    @database_sync_to_async
    def save_message(self, user, message_text):
        Room = apps.get_model('base', 'Room')
        Message = apps.get_model('base', 'Message')
        Notification = apps.get_model('base', 'Notification')

        room = Room.objects.get(id=self.room_id)

        # Add user to room participants (if you have a participants field)
        # If not, we'll just track by messages
        if hasattr(room, 'participants'):
            room.participants.add(user)

        message = Message.objects.create(
            user=user,
            room=room,
            body=message_text
        )

        # 🔔 CREATE COMMENT NOTIFICATION
        if room.host != user:
            Notification.objects.create(
                user=room.host,
                sender=user,
                room=room,
                type='comment'
            )

        return message