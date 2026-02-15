from django.contrib import admin

# Register your models here.
from .models import User #importing the custom user model that we created in models.py file
admin.site.register(User)#registering the custom user model that we created in models.py file to the admin site so that we can see the custom user model in the admin site and we can also add,edit and delete the custom user model in the admin site

