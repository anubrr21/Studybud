import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.apps import apps
from django.utils import timezone
from django.contrib.auth import get_user_model

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'room_{self.room_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Send current participants list and pinned messages to the newly connected user
        await self.send_pinned_messages()
        await self.send_participants_update()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope["user"]
        
        # Handle different message types
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            message_text = data['message']
            parent_id = data.get('parent_id')
            message = await self.save_message(user, message_text, parent_id)
            
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
                    'parent_id': message.parent_message.id if message.parent_message else None,
                    'reply_count': message.reply_count,
                    'is_pinned': message.is_pinned,
                }
            )
            
            # Send updated participants list to everyone
            await self.send_participants_update()
            
        elif message_type == 'pin_message':
            message_id = data['message_id']
            success = await self.pin_message(user, message_id)
            if success:
                await self.send_pinned_messages()
                
        elif message_type == 'unpin_message':
            message_id = data['message_id']
            success = await self.unpin_message(user, message_id)
            if success:
                await self.send_pinned_messages()

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
            'message_id': event['message_id'],
            'avatar': event['avatar'],
            'parent_id': event['parent_id'],
            'reply_count': event['reply_count'],
            'is_pinned': event['is_pinned'],
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

    async def send_pinned_messages(self):
        """Send pinned messages to all users"""
        pinned_data = await self.get_pinned_messages()
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'pinned_messages_update',
                'pinned_messages': pinned_data['pinned_messages'],
                'count': pinned_data['count']
            }
        )

    async def pinned_messages_update(self, event):
        """Send pinned messages update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'pinned_messages_update',
            'pinned_messages': event['pinned_messages'],
            'count': event['count']
        }))

    @database_sync_to_async
    def get_room_participants(self):
        """Get all participants who have sent messages in this room"""
        Room = apps.get_model('base', 'Room')
        Message = apps.get_model('base', 'Message')
        User = get_user_model()
        
        room = Room.objects.get(id=self.room_id)
        
        # Get unique users who have sent messages in this room
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
    def get_pinned_messages(self):
        """Get all pinned messages in this room"""
        Room = apps.get_model('base', 'Room')
        Message = apps.get_model('base', 'Message')
        
        room = Room.objects.get(id=self.room_id)
        pinned_messages = Message.objects.filter(room=room, is_pinned=True).order_by('-pinned_at')[:3]
        
        messages_list = []
        for msg in pinned_messages:
            messages_list.append({
                'id': msg.id,
                'body': msg.body[:100] + '...' if len(msg.body) > 100 else msg.body,
                'username': msg.user.username,
                'user_id': msg.user.id,
                'created': msg.created.isoformat(),
                'pinned_by': msg.pinned_by.username if msg.pinned_by else None,
            })
        
        return {
            'pinned_messages': messages_list,
            'count': len(messages_list)
        }

    @database_sync_to_async
    def pin_message(self, user, message_id):
        """Pin a message (max 3)"""
        Message = apps.get_model('base', 'Message')
        Room = apps.get_model('base', 'Room')
        
        try:
            message = Message.objects.get(id=message_id)
            room = Room.objects.get(id=self.room_id)
            
            # Check if already pinned
            if message.is_pinned:
                return False
            
            # Check current pinned count
            pinned_count = Message.objects.filter(room=room, is_pinned=True).count()
            if pinned_count >= 3:
                return False
            
            message.is_pinned = True
            message.pinned_at = timezone.now()
            message.pinned_by = user
            message.save()
            
            # Also add to room's pinned_messages
            if hasattr(room, 'pinned_messages'):
                room.pinned_messages.add(message)
            
            return True
        except Exception as e:
            print(f"Error pinning message: {e}")
            return False

    @database_sync_to_async
    def unpin_message(self, user, message_id):
        """Unpin a message"""
        Message = apps.get_model('base', 'Message')
        Room = apps.get_model('base', 'Room')
        
        try:
            message = Message.objects.get(id=message_id)
            room = Room.objects.get(id=self.room_id)
            
            message.is_pinned = False
            message.pinned_at = None
            message.pinned_by = None
            message.save()
            
            # Remove from room's pinned_messages
            if hasattr(room, 'pinned_messages'):
                room.pinned_messages.remove(message)
            
            return True
        except Exception as e:
            print(f"Error unpinning message: {e}")
            return False

    @database_sync_to_async
    def save_message(self, user, message_text, parent_id=None):
        Room = apps.get_model('base', 'Room')
        Message = apps.get_model('base', 'Message')
        Notification = apps.get_model('base', 'Notification')

        room = Room.objects.get(id=self.room_id)
        
        parent_message = None
        if parent_id:
            try:
                parent_message = Message.objects.get(id=parent_id)
            except Message.DoesNotExist:
                parent_message = None

        message = Message.objects.create(
            user=user,
            room=room,
            body=message_text,
            parent_message=parent_message
        )

        # Update reply count on parent message
        if parent_message:
            parent_message.reply_count = parent_message.replies.count()
            parent_message.save()

        # Add user to room participants if field exists
        if hasattr(room, 'participants'):
            room.participants.add(user)

        # 🔔 CREATE COMMENT NOTIFICATION
        if room.host != user:
            Notification.objects.create(
                user=room.host,
                sender=user,
                room=room,
                message=message,
                notification_type='comment'  # Make sure this field name matches your model
            )

        return message