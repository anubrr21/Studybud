from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
import base64
from django.core.files.base import ContentFile
from PIL import Image
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
    avatar = models.TextField(null=True, blank=True)
    followers = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="following",
        blank=True
    )

    # default image for the user profile picture when the user does not upload one
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # this is required when we change the USERNAME_FIELD to email.it specifies the fields that are required when creating a superuser account using the createsuperuser command in django shell.since we have set it to an empty list there are no additional fields required when creating a superuser account using the createsuperuser command in django shell.
    objects = CustomUserManager()

    @property
    def avatar_url(self):
        if self.avatar_base64:
            return f"data:image/jpeg;base64,{self.avatar_base64}"
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
            self.save()
            return True
        except Exception as e:
            print(f"Error saving avatar: {e}")
            return False


class Topic(models.Model):  # topic model for different topics of rooms
    name = models.CharField(max_length=200)  # name field for the topic

    def __str__(self):
        return self.name  # string represntation of the topic model
    


# creating a room first
class Room(models.Model):  # a topic can have many rooms but a room can have only one topic(hence foreign key relationship)
    host = models.ForeignKey(User, on_delete=models.CASCADE)  # user who created the room.one to many relatioship.one user can create many rooms
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)  # many to one relationship.one topic can have many rooms but one room can only have one topic
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)  # database cannot have an instance of the model here and this can be left blank
    participants = models.ManyToManyField(User, related_name='participants', blank=True)  # stores the current users in the room
    likes = models.ManyToManyField(User, related_name="liked_rooms", blank=True)
    updated = models.DateTimeField(auto_now=True)  # whenever we update the model this field will be updated automatically.takes timestamp every single time the model is saved
    created = models.DateTimeField(auto_now_add=True)  # when the model is created this field will be set automatically. gives the timestamp of creation
    pinned_messages = models.ManyToManyField('Message', related_name='pinned_in_rooms', blank=True)

    # id=models.BigAutoField(primary_key=True,auto_created=True,serialize=False,verbase_name='ID')#primary key field for the model
    class Meta:  # meta class to specify the ordering of the model instances.to print the newest rooms first
        ordering = ['-updated', '-created']  # negative sign indicates descending order

    def __str__(self):  # python claass is created.this method returns the string representation of the model
        return self.name


class Message(models.Model):  # messge model for chat messages in the room
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # user who sent the message.one to many relationship.one user can send many messgaes
    room = models.ForeignKey(Room, on_delete=models.CASCADE)  # many to one relationship.many messages can be sent in one room
    body = models.TextField()  # body of the message

    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    reply_count = models.IntegerField(default=0)

    is_pinned = models.BooleanField(default=False)
    pinned_at = models.DateTimeField(null=True, blank=True)
    pinned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pinned_messages')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:  # meta class to specify the ordering of the model instances.to print the newest rooms first
        ordering = ['-is_pinned', '-created']  # negative sign indicates descending order

    def __str__(self):
        return self.body[0:50]  # returning the first 50 characters of the message

    def save(self, *args, **kwargs):
        # Update reply count on parent message
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
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)  # Added missing message field
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.sender} {self.type} {self.room}"