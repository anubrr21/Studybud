from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm  
from .models import Room, User
from django import forms

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']


class UserForm(forms.ModelForm):
    avatar_upload = forms.ImageField(required=False, label='Profile Picture')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'bio', 'avatar_upload']
        # Note: 'avatar' field is not included here because we're using avatar_upload instead
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email read-only to prevent changes
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['email'].help_text = 'Email cannot be changed'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        avatar_file = self.cleaned_data.get('avatar_upload')
        
        if avatar_file:
            # Call the model method to save avatar as base64
            user.save_avatar_from_file(avatar_file)
        
        if commit:
            user.save()
        return user