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

            parent_info = None
            if message.parent_message:
             parent_info = {
                'id': message.parent_message.id,
                'username': message.parent_message.user.username,
                'body': message.parent_message.body[:50] + ('...' if len(message.parent_message.body) > 50 else '')
            }
            
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
                    'parent_info':parent_info,
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
        # Also send a message update to refresh the pin icon
           await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'pin_status_update',
                'message_id': message_id,
                'is_pinned': True
            }
        )
                
        elif message_type == 'unpin_message':
         message_id = data['message_id']
         success = await self.unpin_message(user, message_id)
         if success:
          await self.send_pinned_messages()
        # Also send a message update to refresh the pin icon
          await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'pin_status_update',
                'message_id': message_id,
                'is_pinned': False
            }
        )
    async def pin_status_update(self, event):
     """Send pin status update to WebSocket"""
     await self.send(text_data=json.dumps({
        'type': 'pin_status_update',
        'message_id': event['message_id'],
        'is_pinned': event['is_pinned']
    }))
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
            'message_id': event['message_id'],
            'avatar': event['avatar'],
            'parent_id': event['parent_id'],
            'parent_info':event['parent_info'],
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
                type='comment'  # Make sure this field name matches your model
            )

        return message
    

class PersonalChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Check if user is participant in this chat
        if not await self.is_participant():
            await self.close()
            return
        
        self.chat_group_name = f'personal_chat_{self.chat_id}'
        
        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send typing status
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'user_online',
                'user_id': self.user.id,
                'username': self.user.username
            }
        )
        
        # Mark messages as delivered
        await self.mark_messages_delivered()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'chat_group_name'):
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'user_offline',
                    'user_id': self.user.id,
                    'username': self.user.username
                }
            )
            
            await self.channel_layer.group_discard(
                self.chat_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            # Send message
            message = await self.save_message(
                data['content'],
                parent_id=data.get('parent_id')
            )
            
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'message_id': message.id,
                    'sender_id': message.sender.id,
                    'sender_username': message.sender.username,
                    'sender_avatar': message.sender.avatar_url,
                    'content': message.content,
                    'parent_id': message.parent_message.id if message.parent_message else None,
                    'created': message.created.isoformat()
                }
            )
            
        elif message_type == 'typing':
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'user_typing',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'is_typing': data['is_typing']
                }
            )
            
        elif message_type == 'read':
            await self.mark_message_read(data['message_id'])
            
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'message_read',
                    'message_id': data['message_id'],
                    'user_id': self.user.id
                }
            )
            
        elif message_type == 'reaction':
            if data['action'] == 'add':
                await self.add_reaction(data['message_id'], data['reaction'])
            else:
                await self.remove_reaction(data['message_id'], data['reaction'])
            
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'message_reaction',
                    'message_id': data['message_id'],
                    'user_id': self.user.id,
                    'reaction': data['reaction'],
                    'action': data['action']
                }
            )
            
        elif message_type == 'pin':
            await self.pin_message(data['message_id'])
            
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'message_pinned',
                    'message_id': data['message_id'],
                    'is_pinned': True
                }
            )
            
        elif message_type == 'unpin':
            await self.unpin_message(data['message_id'])
            
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'message_pinned',
                    'message_id': data['message_id'],
                    'is_pinned': False
                }
            )
            
        elif message_type == 'delete':
            delete_for = data.get('delete_for', 'everyone')
            await self.delete_message(data['message_id'], delete_for)
            
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'message_deleted',
                    'message_id': data['message_id'],
                    'deleted_for': delete_for,
                    'user_id': self.user.id
                }
            )
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message_id': event['message_id'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'sender_avatar': event['sender_avatar'],
            'content': event['content'],
            'parent_id': event['parent_id'],
            'created': event['created']
        }))
    
    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_typing': event['is_typing']
        }))
    
    async def user_online(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_online',
            'user_id': event['user_id'],
            'username': event['username']
        }))
    
    async def user_offline(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_offline',
            'user_id': event['user_id'],
            'username': event['username']
        }))
    
    async def message_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_read',
            'message_id': event['message_id'],
            'user_id': event['user_id']
        }))
    
    async def message_reaction(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_reaction',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'reaction': event['reaction'],
            'action': event['action']
        }))
    
    async def message_pinned(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_pinned',
            'message_id': event['message_id'],
            'is_pinned': event['is_pinned']
        }))
    
    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id'],
            'deleted_for': event['deleted_for'],
            'user_id': event['user_id']
        }))
    
    @database_sync_to_async
    def is_participant(self):
        Chat = apps.get_model('base', 'Chat')
        try:
            chat = Chat.objects.get(id=self.chat_id)
            return self.user in chat.participants.all()
        except Chat.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content, parent_id=None):
        Chat = apps.get_model('base', 'Chat')
        ChatMessage = apps.get_model('base', 'ChatMessage')
        ChatParticipant = apps.get_model('base', 'ChatParticipant')
        
        chat = Chat.objects.get(id=self.chat_id)
        
        parent_message = None
        if parent_id:
            try:
                parent_message = ChatMessage.objects.get(id=parent_id)
            except ChatMessage.DoesNotExist:
                pass
        
        message = ChatMessage.objects.create(
            chat=chat,
            sender=self.user,
            content=content,
            parent_message=parent_message
        )
        
        # Update chat's updated time
        chat.save()
        
        # Mark as delivered to other participants
        other_participants = chat.participants.exclude(id=self.user.id)
        for participant in other_participants:
            message.delivered_to.add(participant)
        
        return message
    
    @database_sync_to_async
    def mark_messages_delivered(self):
        Chat = apps.get_model('base', 'Chat')
        ChatMessage = apps.get_model('base', 'ChatMessage')
        
        chat = Chat.objects.get(id=self.chat_id)
        unread_messages = chat.messages.exclude(sender=self.user).exclude(delivered_to=self.user)
        
        for message in unread_messages:
            message.delivered_to.add(self.user)
    
    @database_sync_to_async
    def mark_message_read(self, message_id):
        ChatMessage = apps.get_model('base', 'ChatMessage')
        ChatParticipant = apps.get_model('base', 'ChatParticipant')
        
        message = ChatMessage.objects.get(id=message_id)
        message.read_by.add(self.user)
        
        # Update last read message for participant
        participant_info, _ = ChatParticipant.objects.get_or_create(
            chat=message.chat,
            user=self.user
        )
        participant_info.last_read_message = message
        participant_info.save()
    
    @database_sync_to_async
    def add_reaction(self, message_id, reaction):
        ChatMessage = apps.get_model('base', 'ChatMessage')
        message = ChatMessage.objects.get(id=message_id)
        message.add_reaction(self.user, reaction)
    
    @database_sync_to_async
    def remove_reaction(self, message_id, reaction):
        ChatMessage = apps.get_model('base', 'ChatMessage')
        message = ChatMessage.objects.get(id=message_id)
        message.remove_reaction(self.user, reaction)
    
    @database_sync_to_async
    def pin_message(self, message_id):
        ChatMessage = apps.get_model('base', 'ChatMessage')
        message = ChatMessage.objects.get(id=message_id)
        message.is_pinned = True
        message.pinned_at = timezone.now()
        message.save()
    
    @database_sync_to_async
    def unpin_message(self, message_id):
        ChatMessage = apps.get_model('base', 'ChatMessage')
        message = ChatMessage.objects.get(id=message_id)
        message.is_pinned = False
        message.pinned_at = None
        message.save()
    
    @database_sync_to_async
    def delete_message(self, message_id, delete_for):
        ChatMessage = apps.get_model('base', 'ChatMessage')
        message = ChatMessage.objects.get(id=message_id)
        
        if message.sender != self.user:
            return
        
        if delete_for == 'everyone':
            message.deleted_for_everyone = True
            message.deleted_at = timezone.now()
            message.save()
        else:  # delete for me
            message.deleted_for_sender = True
            message.save()