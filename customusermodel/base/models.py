from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser #inheriting from the default user model provided by django
class User(AbstractUser):#creating a custom user model by inheriting from the deault user model provided by django
    name=models.CharField(max_length=200,null=True)#adding a name field to the custom user model 
    email=models.EmailField(unique=True)
    bio=models.TextField(null=True)
    USERNAME_FIELD='email'#telling django to use email as the username field instead of the default username field provided by django
    REQUIRED_FIELDS=[]#this is reqquired when we are using a custom user model and we are using email as the username field instead of the default username field provided by django 
