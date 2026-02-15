from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    name=models.CharField(max_length=200,null=True)
    email=models.EmailField(null=True,unique=True)
    bio=models.TextField(null=True)
    avatar=models.ImageField(null=True,default='avatar.svg')#default image for the user profile picture when the user does not upload one

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]#this is required when we change the USERNAME_FIELD to email.it specifies the fields that are required when creating a superuser account using the createsuperuser command in django shell.since we have set it to an empty list there are no additional fields required when creating a superuser account using the createsuperuser command in django shell.

class Topic(models.Model):#topic model for different topics of rooms
    name=models.CharField(max_length=200)#name field for the topic
    def __str__(self):
      return self.name#string represntation of the topic model 
 #creating a room first
class Room(models.Model): #a topic can have many rooms but a room can have only one topic(hence foreign key relationship)
 host=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)#user who created the room.one to many relatioship.one user can create many rooms
 topic=models.ForeignKey(Topic,on_delete=models.SET_NULL,null=True)#many to one relationship.one topic can have many rooms but one room can only have one topic
 name=models.CharField(max_length=200)
 description=models.TextField(null=True,blank=True)#database cannot have an instance of the model here and this can be left blank
 participants=models.ManyToManyField(User,related_name='participants',blank=True)#stores the current users in the room 
 updated=models.DateTimeField(auto_now=True)#whenever we update the model this field will be updated automatically.takes timestamp every single time the model is saved
 created=models.DateTimeField(auto_now_add=True)#when the model is created this field will be set automatically. gives the timestamp of creation
#id=models.BigAutoField(primary_key=True,auto_created=True,serialize=False,verbase_name='ID')#primary key field for the model
 class Meta:#meta class to specify the ordering of the model instances.to print the newest rooms first
    ordering=['-updated','-created']#negative sign indicates descending order
 def __str__(self): #python claass is created.this method returns the string representation of the model 
  return self.name

class Message(models.Model):#messge model for chat messages in the room
   user=models.ForeignKey(User,on_delete=models.CASCADE)#user who sent the message.one to many relationship.one user can send many messgaes
   room=models.ForeignKey(Room,on_delete=models.CASCADE)#many to one relationship.many messages can be sent in one room  
   body=models.TextField()#body of the message
   updated=models.DateTimeField(auto_now=True)
   created=models.DateTimeField(auto_now_add=True)

   class Meta:#meta class to specify the ordering of the model instances.to print the newest rooms first
    ordering=['-updated','-created']#negative sign indicates descending order
   
   def __str__(self):
     return self.body[0:50]#returning the first 50 characters of the message