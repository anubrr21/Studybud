from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse


from .models import Room,Topic,Message,User,Notification #importing the room model from models.py
from .forms import RoomForm,UserForm,MyUserCreationForm


#creating a dictionary for the rooms templates
#rooms=[
#    {'id':1, 'name':'Lets learn Django!'},
 #    {'id':2, 'name':'Design with me!'},
 #    {'id':3, 'name':'Frontend developers!'}
#     ]

def loginPage(request):
    page='login'
    if request.user.is_authenticated:
         return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
            return render(request, 'base/login_register.html',{'page':page})

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exist')
           
    return render(request, 'base/login_register.html',{'page':page})

def logoutUser(request):
     logout(request)
     return redirect('home')
def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')

    return render(request, 'base/login_register.html', {'form': form})



     
     
def home(request):
    q=request.GET.get('q') if request.GET.get('q')!=None else ''#getting the value of the search query from the request object.if there is no query then set it to an empty string
    rooms=Room.objects.filter(
      Q(topic__name__icontains=q) |
      Q(name__icontains=q)|
      Q(description__icontains=q)
      )#query to get all the rooms from the database.objects is the model manager and all() is a method that retrieves all th objects from the database
    topics=Topic.objects.all()[0:5]#getting all the topics from the database
    room_count=rooms.count()#getting the count of the rooms
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=q)) #getting all the messages
    context={'rooms':rooms,'topics':topics,
    'room_count':room_count,'room_messages':room_messages}#creating a context dictinary to pass the rooms to the template
    return render(request,'base/home.html',context)#calling the rooms dictionary to home.html
def room(request,pk):
        room=Room.objects.get(id=pk)#getting the room with the sepcific id(primary key)
        room_messages=room.message_set.all()#getting all the messages related to the room 
        participants=room.participants.all()
        if request.method=='POST':
             message=Message.objects.create(
                  user=request.user,
                  room=room,
                  body=request.POST.get('body')
             ) 
             room.participants.add(request.user)
             return redirect('room',pk=room.id)
        context={'room':room,'room_messages':room_messages,'participants':participants}#creating a context dictionary to pass the room to the template
        return render(request,'base/room.html',context)
def userProfile(request,pk):
     user = User.objects.get(id=pk)
     rooms=user.room_set.all()#getting all the rooms created by the user
     room_messages=user.message_set.all()#getting all the messages created by the user
     topics=Topic.objects.all()

     
     context={'user': user,'rooms':rooms,
              'room_messages':room_messages,'topics':topics}
     return render(request,'base/profile.html',context)
@login_required(login_url='login')#decorator to restrict access to the view to only logged in users
def createRoom(request):
      form=RoomForm()#creating an instance of the RoommForm
      topics = Topic.objects.all()
      if request.method=='POST':
            topic_name=request.POST.get('topic')#getting the topic name from the request object 
            topic,created=Topic.objects.get_or_create(name=topic_name)#getting the topic object from the database or creating a new one if it doesn't exist 
            Room.objects.create(
                 host=request.user,
                 topic=topic,
                 name=request.POST.get('name'),
                 description=request.POST.get('description')
            )
            return redirect('home')
                

      context={'form':form, 'topics':topics,'room':room}
      return render(request,'base/room_form.html',context)
@login_required(login_url='login')
def updateRoom(request,pk):
      room=Room.objects.get(id=pk)#getting the room with the speicific id(primary key)
      form=RoomForm(instance=room)#creating an instance of the RoomForm with the room instance.this will be prefilled with the room data
      topics = Topic.objects.all()
      if request.user!=room.host:
           return HttpResponse('You are not allowed here!!')
      if request.method=='POST':
             topic_name=request.POST.get('topic')#getting the topic name from the request object 
             topic,created=Topic.objects.get_or_create(name=topic_name)#getting the topic object from the database or creating a new one if it doesn't exist
             room.name=request.POST.get('name')
             room.topic=topic
             room.description=request.POST.get('description')
             room.save()
             return redirect('home')
      context={'form':form,'topics':topics}
      return render(request,'base/room_form.html',context)
@login_required(login_url='login')
def deleteRoom(request,pk):
      room=Room.objects.get(id=pk)#which room to delete
      if request.user!=room.host:
           return HttpResponse('You are not allowed here!!')
      if request.method=='POST':
            room.delete()#deleting the room from the database
            return redirect('home')
      return render(request,'base/delete.html',{'obj':room})   
@login_required(login_url='login')
def deleteMessage(request,pk):
      message=Message.objects.get(id=pk)#which room to delete
      if request.user != message.user:
           return HttpResponse('You are not allowed here!!')
      if request.method=='POST':
            message.delete()#deleting the room from the database
            return redirect('home')
      return render(request,'base/delete.html',{'obj':message})     
@login_required(login_url='login')
def updateUser(request):
       user=request.user
       form=UserForm(instance=user)
       if request.method == 'POST': 
            form=UserForm(request.POST,request.FILES,instance=user)
            if form.is_valid():
                 form.save()
                 return redirect('user-profile',pk=user.id)
       return render(request,'base/update-user.html',{'form':form})
def topicsPage(request):
     q=request.GET.get('q') if request.GET.get('q')!=None else '' 
     topics=Topic.objects.filter(name__icontains=q)#filtering the topics based on the search query 
     return render(request,'base/topics.html',{'topics':topics})
def activityPage(request):
     room_messages=Message.objects.all()
     return render(request,'base/activity.html',{'room_messages':room_messages})

@login_required(login_url='login')
def toggle_like(request, pk):
    room = Room.objects.get(id=pk)

    if request.user in room.likes.all():
        room.likes.remove(request.user)
        liked = False
    else:
        room.likes.add(request.user)
        liked = True

        # 🔔 CREATE NOTIFICATION (ONLY IF NOT SELF-LIKE)
        if room.host != request.user:
            Notification.objects.create(
                user=room.host,
                sender=request.user,
                room=room,
                type='like'
            )

    return JsonResponse({
        "liked": liked,
        "total_likes": room.likes.count()
    })

@login_required
def notifications(request):
    notifications = request.user.notifications.all()

    # mark all as read
    notifications.update(is_read=True)

    return render(request, 'base/notifications.html', {
        'notifications': notifications
    })




