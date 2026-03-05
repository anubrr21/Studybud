from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from PIL import Image
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