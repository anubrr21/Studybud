from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .tokens import email_verification_token, generate_verification_code

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
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        login_input = request.POST.get('email', '').lower().strip()
        password = request.POST.get('password', '')

        if not login_input or not password:
            messages.error(request, 'Please fill in all fields')
            return render(request, 'base/login_register.html', {'page': page})

        # Check if user exists
        try:
            if '@' in login_input:
                user = User.objects.get(email=login_input)
            else:
                user = User.objects.get(username=login_input)
        except User.DoesNotExist:
            messages.error(request, 'This username/email is not registered')
            return render(request, 'base/login_register.html', {'page': page})

        # Check password
        user = authenticate(request, email=user.email, password=password)

        if user is not None:
            login(request, user)
            request.session['welcome_message'] = f'Welcome back, {user.username}!'
            request.session['welcome_type'] = 'returning'
            return redirect('home')
        else:
            messages.error(request, 'Incorrect password')
           
    return render(request, 'base/login_register.html', {'page': page})
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        login_input = request.POST.get('email', '').lower().strip()
        password = request.POST.get('password', '')

        if not login_input or not password:
            messages.error(request, 'Please fill in all fields')
            return render(request, 'base/login_register.html', {'page': page})

        # Try to find user by email or username
        try:
            if '@' in login_input:  # It's an email
                user = User.objects.get(email=login_input)
            else:  # It's a username
                user = User.objects.get(username=login_input)
        except User.DoesNotExist:
            messages.error(request, 'Invalid email/username or password')
            return render(request, 'base/login_register.html', {'page': page})

        user = authenticate(request, email=user.email, password=password)

        if user is not None:
            login(request, user)
            request.session['welcome_message'] = f'Welcome back, {user.username}!'
            request.session['welcome_type'] = 'returning'
            return redirect('home')
        else:
            messages.error(request, 'Invalid email/username or password')
           
    return render(request, 'base/login_register.html', {'page': page})
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').lower().strip()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'Please fill in all fields')
            return render(request, 'base/login_register.html', {'page': page})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'base/login_register.html', {'page': page})

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            # Add a special message for the toast
            request.session['welcome_message'] = f'Welcome back, {user.username}!'
            request.session['welcome_type'] = 'returning'
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password')
           
    return render(request, 'base/login_register.html', {'page': page})
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').lower().strip()
        password = request.POST.get('password', '')

        # Check if fields are empty
        if not email or not password:
            messages.error(request, 'Please fill in all fields')
            return render(request, 'base/login_register.html', {'page': page})

        try:
            # Try to find the user
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'base/login_register.html', {'page': page})

        # Authenticate the user
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Successful login
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password')
           
    return render(request, 'base/login_register.html', {'page': page})
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
            return render(request, 'base/login_register.html', {'page': page})

        user = authenticate(request, email=email, password=password)

        if user is not None:
            # TEMPORARY FIX: Auto-verify dummy emails
            dummy_emails = ['anubrata@gmail.com', 'ashtu@gmail.com', 'anuyz@gmail.com']
            if email in dummy_emails:
                user.email_verified = True
                user.email_verification_token = None
                user.save()
                login(request, user)
                return redirect('home')
            
            # Normal verification flow for other users
            if not user.email_verified:
                messages.warning(request, 'Please verify your email first')
                return redirect('verify-email', user_id=user.id)
            else:
                login(request, user)
                return redirect('home')
        else:
            messages.error(request, 'Invalid email or password')
           
    return render(request, 'base/login_register.html', {'page': page})
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
            return render(request, 'base/login_register.html', {'page': page})

        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Only redirect to verification if email is NOT verified AND token exists
            if not user.email_verified and user.email_verification_token:
                messages.warning(request, 'Please verify your email first')
                return redirect('verify-email', user_id=user.id)
            elif not user.email_verified and not user.email_verification_token:
                # This shouldn't happen, but just in case
                user.email_verification_token = generate_verification_code()
                user.save()
                # Send new verification email
                subject = 'Verify your StudyBud account'
                message = f'Your verification code is: {user.email_verification_token}'
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                messages.info(request, 'A new verification code has been sent to your email')
                return redirect('verify-email', user_id=user.id)
            else:
                login(request, user)
                return redirect('home')
        else:
            messages.error(request, 'Invalid email or password')
           
    return render(request, 'base/login_register.html', {'page': page})
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
            # Check if email is verified
            if user.email_verified:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Please verify your email first')
                return redirect('verify-email', user_id=user.id)
        else:
            messages.error(request, 'Username OR password does not exist')
           
    return render(request, 'base/login_register.html',{'page':page})

def logoutUser(request):
     logout(request)
     return redirect('home')

def registerPage(request):
    page = 'register'
    form = MyUserCreationForm()

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email = user.email.lower()
            user.email_verified = True
            user.email_verification_token = None
            user.save()
            
            login(request, user)
            # Add welcome message for new user
            request.session['welcome_message'] = f'Welcome, {user.username}!'
            request.session['welcome_type'] = 'new'
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    
    context = {'form': form, 'page': page}
    return render(request, 'base/login_register.html', context)
    page = 'register'
    form = MyUserCreationForm()

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email = user.email.lower()
            
            # NEW USERS ARE AUTO-VERIFIED FOR NOW (until email works)
            user.email_verified = True
            user.email_verification_token = None
            user.save()
            
            # Log the user in immediately
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        else:
            # Form is invalid - show errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    context = {'form': form, 'page': page}
    return render(request, 'base/login_register.html', context)
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            # TEMPORARILY AUTO-VERIFY
            user.email_verified = True
            user.email_verification_token = None
            user.save()
            
            # Skip email sending for now
            messages.success(request, 'Account created successfully!')
            login(request, user)
            return redirect('home')

    return render(request, 'base/login_register.html', {'form': form})
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email_verified = False
            user.save()
            
            # Generate verification code
            verification_code = generate_verification_code()
            user.email_verification_token = verification_code
            user.save()
            
            # Send verification email with error handling
            try:
                subject = 'Verify your StudyBud account'
                message = f'Welcome to StudyBud! Your verification code is: {verification_code}'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [user.email]
                
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                messages.success(request, 'Account created! Please check your email for verification code.')
            except Exception as e:
                messages.error(request, f'Account created but email could not be sent: {str(e)}')
                # Still allow them to proceed to verification page
                
            return redirect('verify-email', user_id=user.id)

    return render(request, 'base/login_register.html', {'form': form})
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email_verified = False  # Set email as not verified initially
            user.save()
            
            # Generate verification code
            verification_code = generate_verification_code()
            user.email_verification_token = verification_code
            user.save()
            
            # Send verification email
            subject = 'Verify your StudyBud account'
            message = f'Welcome to StudyBud! Your verification code is: {verification_code}'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            
            messages.success(request, 'Account created! Please verify your email.')
            return redirect('verify-email', user_id=user.id)

    return render(request, 'base/login_register.html', {'form': form})

def verify_email(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Invalid user')
        return redirect('login')
    
    # If user is already verified, redirect to home
    if user.email_verified:
        messages.success(request, 'Your email is already verified!')
        return redirect('home')
    
    if request.method == 'POST':
        entered_code = request.POST.get('verification_code')
        
        if entered_code == user.email_verification_token:
            user.email_verified = True
            user.email_verification_token = None  # Changed from '' to None
            user.save()
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Email verified successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid verification code')
    
    return render(request, 'base/verify_email.html', {'user_id': user_id})
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Invalid user')
        return redirect('login')
    
    if request.method == 'POST':
        entered_code = request.POST.get('verification_code')
        
        if entered_code == user.email_verification_token:
            user.email_verified = True
            user.email_verification_token = ''  # Clear the token
            user.save()
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Email verified successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid verification code')
    
    return render(request, 'base/verify_email.html', {'user_id': user_id})

def resend_verification(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Invalid user')
        return redirect('login')
    
    # Generate new code
    verification_code = generate_verification_code()
    user.email_verification_token = verification_code
    user.save()
    
    # Resend email
    subject = 'Verify your StudyBud account'
    message = f'Your new verification code is: {verification_code}'
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [user.email], fail_silently=False)
    
    messages.success(request, 'Verification code resent!')
    return redirect('verify-email', user_id=user.id)

     
     
def home(request):
    q=request.GET.get('q') if request.GET.get('q')!=None else ''#getting the value of the search query from the request object.if there is no query then set it to an empty string
    rooms=Room.objects.filter(
      Q(topic__name__icontains=q) |
      Q(name__icontains=q)|
      Q(description__icontains=q)
      )#query to get all the rooms from the database.objects is the model manager and all() is a method that retrieves all th objects from the database
    topics=Topic.objects.all()[0:5]#getting all the topics from the database
    room_count=rooms.count()#getting the count of the rooms
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=q)).order_by('-created')[:8] #getting all the messages
    suggested_users=[]
    if request.user.is_authenticated:
         suggested_users=User.objects.exclude(id__in=request.user.following.all()).exclude(id=request.user.id)[:5]#suggesting users to follow excluding the ones the user is already following and excluding the user himself
    welcome_message = request.session.pop('welcome_message', None)
    welcome_type = request.session.pop('welcome_type', None)     
    context={'rooms':rooms,'topics':topics,
    'room_count':room_count,'room_messages':room_messages,'suggested_users':suggested_users,'welcome_message':welcome_message,'welcome_type':welcome_type}#creating a context dictinary to pass the rooms to the template
    return render(request,'base/home.html',context)#calling the rooms dictionary to home.html

@login_required(login_url='login')
def room(request, pk):
    room = get_object_or_404(Room, id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        body = request.POST.get('body')

        if body:
            message = Message.objects.create(
                user=request.user,
                room=room,
                body=body
            )

          

            # Comment notification
            if room.host != request.user:
                Notification.objects.create(
                    user=room.host,
                    sender=request.user,
                    room=room,
                    type='comment'
                )

            # Join notification
            

            # AJAX response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                     "id": message.id,
                    "username": message.user.username,
                    "user_id":message.user.id,
                    "avatar":message.user.avatar_url,
                    "body": message.body
                    
                })

        return redirect('room', pk=room.id)

    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants,
    }

    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    mutual_followers = []

    if request.user.is_authenticated and request.user != user:
        mutual_followers = user.followers.filter(
        id__in=request.user.following.values_list('id', flat=True)
    )

    context = {
        'user': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics,
        'followers': user.followers.all(),
        'following': user.following.all(),
        'mutual_followers': mutual_followers,
    }
    return render(request, 'base/profile.html', context)

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
                

      context={'form':form, 'topics':topics}
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
    q = request.GET.get('q') if request.GET.get('q') else ''

    room_messages = Message.objects.filter(
        Q(user__username__icontains=q) |
        Q(room__name__icontains=q) |
        Q(body__icontains=q)
    ).order_by('-created')

    return render(request, 'base/activity.html', {
        'room_messages': room_messages,
        'search_query': q
    })

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

@login_required(login_url='login')
def mark_notifications_read(request):
    request.user.notifications.update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required(login_url='login')
def toggle_follow(request, pk):
    target_user = User.objects.get(id=pk)

    if request.user == target_user:
        return JsonResponse({"error": "You cannot follow yourself"}, status=400)

    if request.user in target_user.followers.all():
        target_user.followers.remove(request.user)
        following = False
    else:
        target_user.followers.add(request.user)
        following = True

        # 🔔 FOLLOW NOTIFICATION
        Notification.objects.create(
            user=target_user,
            sender=request.user,
            type='follow'
        )

    return JsonResponse({
        "following": following,
        "followers_count": target_user.followers.count()
    })

def profile_followers(request, pk):
    user = User.objects.get(id=pk)
    followers = user.followers.all()

    data = [
        {
            "id": u.id,
            "username": u.username,
            "avatar": u.avatar_url
        }
        for u in followers
    ]

    return JsonResponse({"users": data})


def profile_following(request, pk):
    user = User.objects.get(id=pk)
    following = user.following.all()

    data = [
        {
            "id": u.id,
            "username": u.username,
            "avatar": u.avatar_url
        }
        for u in following
    ]

    return JsonResponse({"users": data})

@login_required(login_url='login')
def edit_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    if request.method == "POST":
        new_body = request.POST.get("body")

        if new_body:
            message.body = new_body
            message.save()

            return JsonResponse({
                "success": True,
                "body": message.body
            })

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required(login_url='login')
def delete_account(request):

    if request.method == "POST":
        password = request.POST.get("password")

        user = authenticate(
            request,
            email=request.user.email,
            password=password
        )

        if user is not None:
            request.user.delete()
            logout(request)
            return redirect('home')
        else:
            messages.error(request, "Incorrect password. Try again.")

    return render(request, 'base/delete_account.html')

@login_required
def pin_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    room = message.room
    
    # Check if user is participant
    if request.user not in room.participants.all() and request.user != room.host:
        return redirect('home')
    
    # Check pin limit
    pinned_count = Message.objects.filter(room=room, is_pinned=True).count()
    if pinned_count < 3:
        message.is_pinned = True
        message.pinned_at = timezone.now()
        message.pinned_by = request.user
        message.save()
        
        # Add to room's pinned messages
        room.pinned_messages.add(message)
    
    return redirect('room', pk=room.id)

@login_required
def unpin_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    room = message.room
    
    message.is_pinned = False
    message.pinned_at = None
    message.pinned_by = None
    message.save()
    
    room.pinned_messages.remove(message)
    
    return redirect('room', pk=room.id)