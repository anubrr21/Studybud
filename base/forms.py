from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm  
from .models import Room,User

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model=User
        fields=['email','password1','password2']


class RoomForm(ModelForm):#creating a form for the room model 
    class Meta:# meta class to specify the model and the fields to be included in the form
        model=Room
        fields='__all__'
        exclude=['host','participants']#excluding the host and participants fields the form as these will be set automatically in the view
class UserForm(ModelForm):
    class Meta:
        model=User
        fields=['avatar','email','bio']