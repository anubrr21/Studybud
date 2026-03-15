from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone
import json
from PIL import Image
from django.contrib.auth.models import User 
import base64
import io

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=200, null=True)
    email = models.EmailField(null=True, unique=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(null=True)
    
    # Change this from ImageField to TextField
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)  # Keep this for backward compatibility
    avatar_base64 = models.TextField(null=True, blank=True)  # Add this new field for base64 storage
    
    followers = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="following",
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    @property
    def avatar_url(self):
        # First try base64
        if self.avatar_base64:
            return f"data:image/jpeg;base64,{self.avatar_base64}"
        # Fall back to regular avatar field
        elif self.avatar:
            try:
                return self.avatar.url
            except:
                pass
        return "/static/images/avatar.svg"
    
    def save_avatar_from_file(self, file):
        """Convert uploaded file to base64 and save"""
        try:
            # Open and resize image to save space
            img = Image.open(file)
            # Resize to max 300x300 to keep database size small
            img.thumbnail((300, 300))
            
            # Convert to JPEG
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=70)
            img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            self.avatar_base64 = img_str
            # Optionally clear the old avatar field
            self.avatar = None
            self.save()
            return True
        except Exception as e:
            print(f"Error saving avatar: {e}")
            return False


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    likes = models.ManyToManyField(User, related_name="liked_rooms", blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    pinned_messages = models.ManyToManyField('Message', related_name='pinned_in_rooms', blank=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()

    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    reply_count = models.IntegerField(default=0)

    is_pinned = models.BooleanField(default=False)
    pinned_at = models.DateTimeField(null=True, blank=True)
    pinned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pinned_messages')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-created']

    def __str__(self):
        return self.body[0:50]

    def save(self, *args, **kwargs):
        if self.parent_message:
            self.parent_message.reply_count = self.parent_message.replies.count()
            self.parent_message.save()
        super().save(*args, **kwargs)


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('join', 'Join'),
        ('follow', 'Follow'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.sender} {self.type} {self.room}"
    

class ChatTheme(models.Model):
    """Theme settings for a chat between two users"""
    name = models.CharField(max_length=100, default="Default")
    background_image = models.ImageField(upload_to='chat_themes/', null=True, blank=True)
    background_color = models.CharField(max_length=20, default="#2d2d39")  # Default dark theme
    message_bubble_user = models.CharField(max_length=20, default="#71c6dd")  # User's messages
    message_bubble_other = models.CharField(max_length=20, default="#3f4156")  # Other's messages
    text_color = models.CharField(max_length=20, default="#e5e5e5")
    timestamp_color = models.CharField(max_length=20, default="#b2bdbd")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_public = models.BooleanField(default=False)  # Can others use this theme?
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Chat(models.Model):
    """Personal chat between two users"""
    participants = models.ManyToManyField(User, related_name='personal_chats')
    theme = models.ForeignKey(ChatTheme, on_delete=models.SET_NULL, null=True, blank=True)
    custom_background = models.ImageField(upload_to='chat_backgrounds/', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated']
    
    def __str__(self):
        return f"Chat between {', '.join([p.username for p in self.participants.all()])}"
    
    def get_other_participant(self, user):
        """Get the other participant in the chat"""
        return self.participants.exclude(id=user.id).first()
    
    def get_last_message(self):
        """Get the last message in the chat"""
        return self.messages.first()

class ChatMessage(models.Model):
    """Individual messages in a personal chat"""
    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System'),
    )
    
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()  # Text content or file URL
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)  # Size in bytes
    file_type = models.CharField(max_length=100, null=True, blank=True)  # MIME type

    thumbnail = models.FileField(upload_to='chat_thumbnails/', null=True, blank=True)
    
    # Reply feature
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    reply_count = models.IntegerField(default=0)
    
    # Pin feature
    is_pinned = models.BooleanField(default=False)
    pinned_at = models.DateTimeField(null=True, blank=True)
    
    # Reactions
    reactions = models.JSONField(default=dict, blank=True)  # {"👍": ["user1", "user2"], "❤️": ["user3"]}
    
    # Read receipts
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)
    delivered_to = models.ManyToManyField(User, related_name='delivered_messages', blank=True)
    
    # Delete features
    deleted_for_sender = models.BooleanField(default=False)
    deleted_for_everyone = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
    
    def save(self, *args, **kwargs):
        if self.parent_message:
            self.parent_message.reply_count = self.parent_message.replies.count()
            self.parent_message.save()
        super().save(*args, **kwargs)
    
    def add_reaction(self, user, reaction):
        """Add a reaction to the message"""
        if reaction not in self.reactions:
            self.reactions[reaction] = []
        if user.username not in self.reactions[reaction]:
            self.reactions[reaction].append(user.username)
        self.save()
    
    def remove_reaction(self, user, reaction):
        """Remove a reaction from the message"""
        if reaction in self.reactions and user.username in self.reactions[reaction]:
            self.reactions[reaction].remove(user.username)
            if not self.reactions[reaction]:
                del self.reactions[reaction]
            self.save()
    
    def mark_as_read(self, user):
        """Mark message as read by user"""
        if user not in self.read_by.all():
            self.read_by.add(user)
    
    def mark_as_delivered(self, user):
        """Mark message as delivered to user"""
        if user not in self.delivered_to.all():
            self.delivered_to.add(user)

class ChatParticipant(models.Model):
    """Additional participant info for each chat"""
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='participant_info')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_read_message = models.ForeignKey(ChatMessage, on_delete=models.SET_NULL, null=True, blank=True)
    muted = models.BooleanField(default=False)
    pinned = models.BooleanField(default=False)  # Pin chat to top
    archived = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['chat', 'user']
    
    def __str__(self):
        return f"{self.user.username} in chat {self.chat.id}"
    
    def get_unread_count(self):
        """Get number of unread messages for this user in this chat"""
        if not self.last_read_message:
            return self.chat.messages.exclude(sender=self.user).count()
        return self.chat.messages.filter(
            created__gt=self.last_read_message.created
        ).exclude(sender=self.user).count()
    


class StudyPlan(models.Model):
    PRIORITY_CHOICES = [
        (1, '🔥 High'),
        (2, '📌 Medium'),
        (3, '📝 Low'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '⏳ Pending'),
        ('in_progress', '▶️ In Progress'),
        ('completed', '✅ Completed'),
        ('overdue', '⚠️ Overdue'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_plans')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=100)
    
    # Date and Time
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    reminder_time = models.DateTimeField(null=True, blank=True)
    
    # Study details
    estimated_hours = models.FloatField(default=1.0)
    actual_hours = models.FloatField(default=0.0)
    
    # Status and Priority
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Recurring plans
    is_recurring = models.BooleanField(default=False)
    recurring_pattern = models.JSONField(null=True, blank=True)  # Store weekly pattern
    
    # Resources
    resources = models.ManyToManyField('StudyResource', blank=True)
    
    # Timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    notification_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['start_date', 'priority']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def duration_hours(self):
        delta = self.end_date - self.start_date
        return delta.total_seconds() / 3600
    
    def progress_percentage(self):
        if self.estimated_hours > 0:
            return min(100, (self.actual_hours / self.estimated_hours) * 100)
        return 0
    
    def is_overdue(self):
        return self.end_date < timezone.now() and self.status != 'completed'

class StudyResource(models.Model):
    RESOURCE_TYPES = [
        ('pdf', '📄 PDF'),
        ('video', '🎥 Video'),
        ('link', '🔗 Link'),
        ('note', '📝 Note'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES)
    
    # File or URL
    file = models.FileField(upload_to='study_resources/', null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    
    # Metadata
    subject = models.CharField(max_length=100)
    duration = models.IntegerField(default=0, help_text="Estimated time in minutes")
    is_public = models.BooleanField(default=False)
    
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class StudySession(models.Model):
    """Track actual study sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(StudyPlan, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0, help_text="Duration in minutes")
    notes = models.TextField(blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.subject} - {self.start_time.date()}"