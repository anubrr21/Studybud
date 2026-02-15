from django.contrib import admin

# Register your models here.
from .models import Room, Topic, Message,User # importing the room model from models.py
admin.site.register(User)#we want to view this item and also work with it in the admin panel 
admin.site.register(Room)# we want to  view this item and also work with it in the admin panel
admin.site.register(Topic)
admin.site.register(Message)
