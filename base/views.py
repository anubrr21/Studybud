from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q,Count,Max
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
from .models import Chat, ChatMessage, ChatTheme, ChatParticipant
from .models import Room,Topic,Message,User,Notification
from .forms import RoomForm,UserForm,MyUserCreationForm
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render
from datetime import datetime,timedelta
from .models import StudyPlan, StudyResource, StudySession
from django.db import models
import os
import mimetypes
import subprocess
import sys
import json 
from PIL import Image
import io
from .emails import send_verification_email, send_password_reset_email
from django.contrib.auth.views import PasswordResetView

# ============================================
# AUTHENTICATION VIEWS
# ============================================

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

        # Check if user exists (by email or username)
        try:
            if '@' in login_input:
                user = User.objects.get(email=login_input)
            else:
                user = User.objects.get(username=login_input)
        except User.DoesNotExist:
            messages.error(request, 'This username/email is not registered')
            return render(request, 'base/login_register.html', {'page': page})

        # Check if email is verified
        if not user.email_verified:
            messages.error(request, 'Please verify your email first. Check your inbox for the verification code.')
            return redirect('verify-email', user_id=user.id)

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
            
            # List of dummy email addresses
            dummy_emails = [
                'anubrata@gmail.com',
                'ashtu@gmail.com', 
                'annnnyyz@gmail.com',
                'anuyz@gmail.com',
            ]
            
            if user.email in dummy_emails:
                user.email_verified = True
                user.email_verification_token = None
                user.save()
                login(request, user)
                request.session['welcome_message'] = f'Welcome, {user.username}!'
                request.session['welcome_type'] = 'new'
                return redirect('home')
            else:
                user.email_verified = False
                user.save()
                
                verification_code = generate_verification_code()
                user.email_verification_token = verification_code
                user.save()
                
                # Get the site URL for email links
                current_site = get_current_site(request)
                site_url = f"{request.scheme}://{current_site.domain}"
                
                # Pass site_url to the email function
                result = send_verification_email(user, verification_code, site_url)
                
                if result['success']:
                    messages.success(request, 'Account created! Please check your email for verification code.')
                else:
                    messages.warning(request, 'Account created but verification email could not be sent. You can request a new code.')
                
                return redirect('verify-email', user_id=user.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    
    context = {'form': form, 'page': page}
    return render(request, 'base/login_register.html', context)

def verify_email(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Invalid user')
        return redirect('login')
    
    if user.email_verified:
        messages.success(request, 'Your email is already verified!')
        return redirect('home')
    
    if request.method == 'POST':
        entered_code = request.POST.get('verification_code')
        
        if entered_code == user.email_verification_token:
            user.email_verified = True
            user.email_verification_token = None
            user.save()
            
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
    
    # Send verification email via Resend
    result = send_verification_email(user, verification_code)
    
    if result['success']:
        messages.success(request, 'Verification code resent! Please check your email.')
    else:
        messages.error(request, 'Failed to send verification code. Please try again.')
    
    return redirect('verify-email', user_id=user.id)


# ============================================
# CUSTOM PASSWORD RESET VIEW
# ============================================

class CustomPasswordResetView(PasswordResetView):
    template_name = 'base/password_reset.html'
    email_template_name = 'base/password_reset_email.html'
    subject_template_name = 'base/password_reset_subject.txt'
    
    def form_valid(self, form):
        # Get the user
        email = form.cleaned_data['email']
        users = User.objects.filter(email=email)
        
        if users.exists():
            user = users.first()
            # Generate reset link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = self.token_generator.make_token(user)
            reset_link = f"{self.request.scheme}://{get_current_site(self.request).domain}/password-reset-confirm/{uid}/{token}/"

             # Get site URL for email links
            current_site = get_current_site(self.request)
            site_url = f"{self.request.scheme}://{current_site.domain}"
            
            # Send via Resend
            send_password_reset_email(user, reset_link)
            
        return redirect('password_reset_done')


# ============================================
# HOME AND ROOM VIEWS
# ============================================

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    # Get ALL rooms for count (unfiltered)
    all_rooms = Room.objects.all()
    total_room_count = all_rooms.count()
    
    # Get filtered rooms for display (but only latest 3)
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    ).order_by('-created')[:3]  # Only get latest 3, ordered by newest first
    
    topics = Topic.objects.all()[0:5]
    room_count = all_rooms.count()  # Use total count, not filtered count
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)).order_by('-created')[:8]
    suggested_users = []
    
    if request.user.is_authenticated:
        suggested_users = User.objects.exclude(id__in=request.user.following.all()).exclude(id=request.user.id)[:5]
    
    welcome_message = request.session.pop('welcome_message', None)
    welcome_type = request.session.pop('welcome_type', None)
    
    # Get unique users count for activity page
    unique_users = Message.objects.values('user').distinct().count()
    
    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': total_room_count,
        'room_messages': room_messages,
        'suggested_users': suggested_users,
        'welcome_message': welcome_message,
        'welcome_type': welcome_type,
        'unique_users': unique_users,
    }
    return render(request, 'base/home.html', context)


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

            if room.host != request.user:
                Notification.objects.create(
                    user=room.host,
                    sender=request.user,
                    room=room,
                    type='comment'
                )

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    "id": message.id,
                    "username": message.user.username,
                    "user_id": message.user.id,
                    "avatar": message.user.avatar_url,
                    "body": message.body
                })

        return redirect('room', pk=room.id)

    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants,
    }

    return render(request, 'base/room.html', context)


# ============================================
# USER PROFILE VIEWS
# ============================================

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


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'base/update-user.html', {'form': form})


# ============================================
# ROOM CRUD VIEWS
# ============================================

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


# ============================================
# TOPICS AND ACTIVITY VIEWS
# ============================================

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activityPage(request):
    q = request.GET.get('q') if request.GET.get('q') else ''
    room_messages = Message.objects.filter(
        Q(user__username__icontains=q) |
        Q(room__name__icontains=q) |
        Q(body__icontains=q)
    ).order_by('-created')
    
    # Get unique users count
    unique_users = room_messages.values('user').distinct().count()
    
    return render(request, 'base/activity.html', {
        'room_messages': room_messages,
        'search_query': q,
        'unique_users': unique_users,
    })


def all_rooms(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    # Filter rooms based on search
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(host__username__icontains=q)
    )
    
    topics = Topic.objects.all()
    room_count = rooms.count()
    
    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'search_query': q,
    }
    return render(request, 'base/all_rooms.html', context)


# ============================================
# LIKE AND NOTIFICATION VIEWS
# ============================================

@login_required(login_url='login')
def toggle_like(request, pk):
    room = Room.objects.get(id=pk)
    if request.user in room.likes.all():
        room.likes.remove(request.user)
        liked = False
    else:
        room.likes.add(request.user)
        liked = True
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
    notifications.update(is_read=True)
    return render(request, 'base/notifications.html', {
        'notifications': notifications
    })


@login_required(login_url='login')
def mark_notifications_read(request):
    request.user.notifications.update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


# ============================================
# FOLLOW SYSTEM VIEWS
# ============================================

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


# ============================================
# MESSAGE EDIT/DELETE VIEWS
# ============================================

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


# ============================================
# PIN MESSAGE VIEWS
# ============================================

@login_required
def pin_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    room = message.room
    if request.user not in room.participants.all() and request.user != room.host:
        return redirect('home')
    pinned_count = Message.objects.filter(room=room, is_pinned=True).count()
    if pinned_count < 3:
        message.is_pinned = True
        message.pinned_at = timezone.now()
        message.pinned_by = request.user
        message.save()
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


# ============================================
# CHAT SYSTEM VIEWS
# ============================================

@login_required
def chats_list(request):
    """Display all personal chats for the user"""
    chats = Chat.objects.filter(participants=request.user).annotate(
        last_message_time=Max('messages__created')
    ).order_by('-last_message_time')
    
    chat_data = []
    total_unread_chats = 0  # Count unread CHATS, not messages
    
    for chat in chats:
        other_user = chat.get_other_participant(request.user)
        last_message = chat.get_last_message()
        participant_info = ChatParticipant.objects.filter(chat=chat, user=request.user).first()
        
        # Get unread count for this chat
        unread_count = participant_info.get_unread_count() if participant_info else 0
        
        # If this chat has unread messages, count it as an unread chat
        if unread_count > 0:
            total_unread_chats += 1
        
        chat_data.append({
            'chat': chat,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count,
            'has_unread': unread_count > 0,
            'last_message_time': chat.updated
        })
    
    context = {
        'chats': chat_data,
        'total_unread_chats': total_unread_chats
    }
    return render(request, 'base/chats.html', context)
   

@login_required
def chat_detail(request, chat_id):
    """Display individual chat page"""
    chat = get_object_or_404(Chat, id=chat_id)
    
    # Check if user is participant
    if request.user not in chat.participants.all():
        return redirect('chats')
    
    other_user = chat.get_other_participant(request.user)
    
    # Get all messages (excluding deleted ones)
    messages = chat.messages.filter(
        Q(deleted_for_everyone=False) &
        (Q(deleted_for_sender=False) | Q(sender=request.user))
    ).select_related('sender', 'parent_message').order_by('created')
    
    # Get pinned messages
    pinned_messages = messages.filter(is_pinned=True).order_by('-pinned_at')
    
    # Mark messages as read
    participant_info, _ = ChatParticipant.objects.get_or_create(
        chat=chat,
        user=request.user
    )
    
    # Update last read message to the latest message
    last_message = messages.last()
    if last_message and last_message.sender != request.user:
        participant_info.last_read_message = last_message
        participant_info.save()
    
    # Get or create default theme
    if not chat.theme:
        default_theme, _ = ChatTheme.objects.get_or_create(
            name="Default",
            defaults={
                'background_color': '#2d2d39',
                'message_bubble_user': '#71c6dd',
                'message_bubble_other': '#3f4156',
                'text_color': '#e5e5e5',
                'timestamp_color': '#b2bdbd'
            }
        )
        chat.theme = default_theme
        chat.save()
    
    # Ensure default themes exist
    ensure_default_themes()
    
    context = {
        'chat': chat,
        'other_user': other_user,
        'messages': messages,
        'pinned_messages': pinned_messages,
        'participant_info': participant_info,
        'themes': ChatTheme.objects.filter(Q(is_public=True) | Q(created_by=request.user))
    }
    return render(request, 'base/chat_detail.html', context)
   

@login_required
def start_chat(request, user_id):
    """Start a new chat with another user"""
    other_user = get_object_or_404(User, id=user_id)
    
    if other_user == request.user:
        return redirect('user-profile', pk=user_id)
    
    # Check if chat already exists
    existing_chat = Chat.objects.filter(
        participants=request.user
    ).filter(participants=other_user).first()
    
    if existing_chat:
        return redirect('chat-detail', chat_id=existing_chat.id)
    
    # Create new chat
    chat = Chat.objects.create()
    chat.participants.add(request.user, other_user)
    
    # Create participant info for both users
    ChatParticipant.objects.create(chat=chat, user=request.user)
    ChatParticipant.objects.create(chat=chat, user=other_user)
    
    return redirect('chat-detail', chat_id=chat.id)


@login_required
def update_chat_theme(request, chat_id):
    """Update chat theme/background"""
    chat = get_object_or_404(Chat, id=chat_id)
    
    if request.user not in chat.participants.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        theme_id = request.POST.get('theme_id')
        custom_bg = request.FILES.get('custom_background')
        
        if theme_id:
            try:
                theme = get_object_or_404(ChatTheme, id=theme_id)
                chat.theme = theme
                chat.custom_background = None  # Clear custom background if theme selected
                chat.save()
                return JsonResponse({'success': True})
            except:
                return JsonResponse({'error': 'Theme not found'}, status=404)
                
        elif custom_bg:
            # Delete old custom background if exists
            if chat.custom_background:
                chat.custom_background.delete(save=False)
            
            chat.custom_background = custom_bg
            chat.theme = None  # Clear theme if custom background uploaded
            chat.save()
            return JsonResponse({'success': True, 'url': chat.custom_background.url})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# ============================================
# CHAT API ENDPOINTS
# ============================================

@login_required
def search_chats(request):
    """API endpoint for searching chats"""
    query = request.GET.get('q', '')
    
    if not query:
        return JsonResponse({'chats': []})
    
    # Search in chat messages and participants
    chats = Chat.objects.filter(
        participants=request.user
    ).filter(
        Q(messages__content__icontains=query) |
        Q(participants__username__icontains=query) |
        Q(messages__created__date__icontains=query)
    ).distinct()
    
    results = []
    for chat in chats:
        other_user = chat.get_other_participant(request.user)
        last_message = chat.get_last_message()
        
        results.append({
            'chat_id': chat.id,
            'other_user': {
                'id': other_user.id,
                'username': other_user.username,
                'avatar': other_user.avatar_url
            },
            'last_message': last_message.content if last_message else '',
            'last_message_time': last_message.created.isoformat() if last_message else None,
            'unread_count': 0  # Will be updated separately
        })
    
    return JsonResponse({'chats': results})


@login_required
def get_unread_chats_count(request):
    """Get total number of chats with unread messages"""
    total_unread_chats = 0
    chats = Chat.objects.filter(participants=request.user)
    
    for chat in chats:
        participant_info = ChatParticipant.objects.filter(chat=chat, user=request.user).first()
        if participant_info and participant_info.get_unread_count() > 0:
            total_unread_chats += 1
    
    return JsonResponse({'unread_chats_count': total_unread_chats})


@login_required
def upload_chat_file(request, chat_id):
    """Handle file uploads in chat"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    chat = get_object_or_404(Chat, id=chat_id)
    
    # Check if user is participant
    if request.user not in chat.participants.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'No file provided'}, status=400)
    
    # Check file size (max 10MB)
    if file.size > 10 * 1024 * 1024:
        return JsonResponse({'error': 'File too large. Max size 10MB.'}, status=400)
    
    # Get file info
    file_name = file.name
    file_size = file.size
    file_type = file.content_type
    
    # Determine message type
    message_type = 'file'
    if file_type.startswith('image/'):
        message_type = 'image'
    
    # Create message
    message = ChatMessage.objects.create(
        chat=chat,
        sender=request.user,
        message_type=message_type,
        content=f"[{message_type.upper()}] {file_name}",
        file=file,
        file_name=file_name,
        file_size=file_size,
        file_type=file_type
    )
    
    # Generate thumbnail for images
    if message_type == 'image':
        try:
            # Open image
            img = Image.open(file)
            
            # Create thumbnail
            img.thumbnail((200, 200))
            
            # Save thumbnail
            thumb_io = io.BytesIO()
            img.save(thumb_io, format='JPEG', quality=70)
            thumb_file = ContentFile(thumb_io.getvalue(), name=f'thumb_{file.name}.jpg')
            
            message.thumbnail.save(f'thumb_{file.name}.jpg', thumb_file, save=True)
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
    
    # Notify via WebSocket
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'personal_chat_{chat_id}',
        {
            'type': 'chat_message',
            'message_id': message.id,
            'sender_id': message.sender.id,
            'sender_username': message.sender.username,
            'sender_avatar': message.sender.avatar_url,
            'content': message.content,
            'message_type': message.message_type,
            'file_url': message.file.url if message.file else None,
            'file_name': message.file_name,
            'file_size': message.file_size,
            'thumbnail_url': message.thumbnail.url if message.thumbnail else None,
            'created': message.created.isoformat()
        }
    )
    
    return JsonResponse({
        'success': True,
        'message_id': message.id,
        'file_url': message.file.url,
        'file_name': file_name,
        'file_size': file_size,
        'message_type': message_type
    })


@login_required
def search_users(request):
    """Search for users to start a chat with"""
    query = request.GET.get('q', '')
    
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(email__icontains=query)
    ).exclude(id=request.user.id)[:20]  # Exclude self, limit to 20
    
    data = {
        'users': [
            {
                'id': user.id,
                'username': user.username,
                'avatar': user.avatar_url
            }
            for user in users
        ]
    }
    return JsonResponse(data)


# ============================================
# CHAT THEME HELPER FUNCTION
# ============================================

def ensure_default_themes():
    """Create default themes if they don't exist"""
    default_themes = [
        # Original Dark Theme (Your default)
        {
            'name': 'StudyBud Dark',
            'background_color': '#2d2d39',
            'message_bubble_user': '#71c6dd',
            'message_bubble_other': '#3f4156',
            'text_color': '#e5e5e5',
            'timestamp_color': '#b2bdbd',
            'is_public': True
        },
        
        # Ocean Blue Theme
        {
            'name': 'Ocean Blue',
            'background_color': '#1e3c72',
            'message_bubble_user': '#00b4d8',
            'message_bubble_other': '#023e8a',
            'text_color': '#ffffff',
            'timestamp_color': '#caf0f8',
            'is_public': True
        },
        
        # Sunset Theme
        {
            'name': 'Sunset',
            'background_color': '#ff6b6b',
            'message_bubble_user': '#feca57',
            'message_bubble_other': '#ff9f4a',
            'text_color': '#2d3436',
            'timestamp_color': '#636e72',
            'is_public': True
        },
        
        # Forest Green Theme
        {
            'name': 'Forest',
            'background_color': '#134e5e',
            'message_bubble_user': '#71c6dd',
            'message_bubble_other': '#0b3b4b',
            'text_color': '#e0f2fe',
            'timestamp_color': '#a5d8ff',
            'is_public': True
        },
        
        # Midnight Purple Theme
        {
            'name': 'Midnight Purple',
            'background_color': '#2c0e37',
            'message_bubble_user': '#ff6f91',
            'message_bubble_other': '#4a1d5e',
            'text_color': '#ffd3e0',
            'timestamp_color': '#ffb3c6',
            'is_public': True
        },
        
        # Cyberpunk Theme
        {
            'name': 'Cyberpunk',
            'background_color': '#0d0221',
            'message_bubble_user': '#00ff9f',
            'message_bubble_other': '#b829fd',
            'text_color': '#ffffff',
            'timestamp_color': '#c77dff',
            'is_public': True
        },
        
        # Matrix Theme
        {
            'name': 'Matrix',
            'background_color': '#0f0f0f',
            'message_bubble_user': '#00ff41',
            'message_bubble_other': '#008f11',
            'text_color': '#00ff41',
            'timestamp_color': '#008f11',
            'is_public': True
        },
        
        # Royal Theme
        {
            'name': 'Royal',
            'background_color': '#1a237e',
            'message_bubble_user': '#ffd700',
            'message_bubble_other': '#0d47a1',
            'text_color': '#ffffff',
            'timestamp_color': '#c5cae9',
            'is_public': True
        },
        
        # Northern Lights Theme
        {
            'name': 'Northern Lights',
            'background_color': '#0a1929',
            'message_bubble_user': '#64ffda',
            'message_bubble_other': '#2979ff',
            'text_color': '#e3f2fd',
            'timestamp_color': '#80deea',
            'is_public': True
        },
        
        # Galaxy Theme
        {
            'name': 'Galaxy',
            'background_color': '#0b0c2b',
            'message_bubble_user': '#9c4dca',
            'message_bubble_other': '#2d1b45',
            'text_color': '#ffffff',
            'timestamp_color': '#8b5cf6',
            'is_public': True
        }
    ]
    
    for theme_data in default_themes:
        ChatTheme.objects.get_or_create(
            name=theme_data['name'],
            defaults=theme_data
        )
def about_us(request):
    """About Us page"""
    return render(request, 'base/about_us.html')

def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, 'base/privacy_policy.html')

def terms_of_service(request):
    """Terms of Service page"""
    return render(request, 'base/terms_of_service.html')

def help_center(request):
    """Help Center page"""
    return render(request, 'base/help_center.html')

def debug_brevo_api(request):
    """Run the Brevo test script and show output"""
    import os
    import requests
    
    output = []
    output.append("<h1>🔍 Brevo API Debug</h1>")
    
    api_key = os.environ.get('BREVO_SMTP_KEY')
    
    output.append(f"<h2>Environment Variable:</h2>")
    output.append(f"<p>BREVO_SMTP_KEY: {'✅ Found' if api_key else '❌ NOT FOUND'}</p>")
    
    if api_key:
        output.append(f"<p>Length: {len(api_key)} characters</p>")
        output.append(f"<p>Starts with: {api_key[:20]}...</p>")
        output.append(f"<p>Ends with: ...{api_key[-10:]}</p>")
        output.append(f"<p>Format: {'✅ xsmtpsib prefix' if api_key.startswith('xsmtpsib') else '❌ wrong prefix'}</p>")
        
        # Test API
        output.append("<h2>Testing API Connection:</h2>")
        headers = {
            "api-key": api_key.strip(),
            "accept": "application/json"
        }
        
        try:
            response = requests.get(
                "https://api.brevo.com/v3/account",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                output.append("<p style='color:green'>✅ API key is VALID!</p>")
                data = response.json()
                output.append(f"<p>Account: {data.get('email', 'N/A')}</p>")
            else:
                output.append(f"<p style='color:red'>❌ API key INVALID! Status: {response.status_code}</p>")
                output.append(f"<p>Response: {response.text}</p>")
        except Exception as e:
            output.append(f"<p style='color:red'>❌ Error: {e}</p>")
    
    return HttpResponse(''.join(output))




@login_required
def study_planner(request):
    """Main study planner view"""
    user = request.user
    
    # Get date from request or default to today
    selected_date = request.GET.get('date')
    if selected_date:
        current_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        current_date = timezone.now().date()
    
    # Get plans for selected date
    day_start = timezone.make_aware(datetime.combine(current_date, datetime.min.time()))
    day_end = timezone.make_aware(datetime.combine(current_date, datetime.max.time()))
    
    plans = StudyPlan.objects.filter(
        user=user,
        start_date__lte=day_end,
        end_date__gte=day_start
    ).order_by('start_date')
    
    # Get upcoming plans
    upcoming_plans = StudyPlan.objects.filter(
        user=user,
        start_date__gt=timezone.now(),
        status='pending'
    ).order_by('start_date')[:5]
    
    # Get overdue plans
    overdue_plans = StudyPlan.objects.filter(
        user=user,
        end_date__lt=timezone.now(),
        status__in=['pending', 'in_progress']
    )
    
    # Update status for overdue plans
    for plan in overdue_plans:
        if plan.status != 'overdue':
            plan.status = 'overdue'
            plan.save()
    
    # Study stats
    total_study_time = StudySession.objects.filter(
        user=user,
        start_time__date=current_date
    ).aggregate(models.Sum('duration'))['duration__sum'] or 0
    
    week_start = current_date - timedelta(days=current_date.weekday())
    week_study_time = StudySession.objects.filter(
        user=user,
        start_time__date__gte=week_start
    ).aggregate(models.Sum('duration'))['duration__sum'] or 0
    
    context = {
        'plans': plans,
        'upcoming_plans': upcoming_plans,
        'overdue_plans': overdue_plans,
        'current_date': current_date,
        'prev_date': current_date - timedelta(days=1),
        'next_date': current_date + timedelta(days=1),
        'total_study_time': total_study_time,
        'week_study_time': week_study_time,
        'subjects': StudyPlan.objects.filter(user=user).values_list('subject', flat=True).distinct(),
    }
    
    return render(request, 'base/study_planner.html', context)

@login_required
def create_study_plan(request):
    """Create a new study plan"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        subject = request.POST.get('subject')
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('end_date')
        end_time = request.POST.get('end_time')
        priority = request.POST.get('priority', 2)
        estimated_hours = request.POST.get('estimated_hours', 1)
        is_recurring = request.POST.get('is_recurring') == 'on'
        
        # Combine date and time
        start_datetime = timezone.make_aware(
            datetime.strptime(f"{start_date} {start_time}", '%Y-%m-%d %H:%M')
        )
        end_datetime = timezone.make_aware(
            datetime.strptime(f"{end_date} {end_time}", '%Y-%m-%d %H:%M')
        )
        
        # Handle recurring pattern
        recurring_pattern = None
        if is_recurring:
            recurring_pattern = {
                'monday': request.POST.get('monday') == 'on',
                'tuesday': request.POST.get('tuesday') == 'on',
                'wednesday': request.POST.get('wednesday') == 'on',
                'thursday': request.POST.get('thursday') == 'on',
                'friday': request.POST.get('friday') == 'on',
                'saturday': request.POST.get('saturday') == 'on',
                'sunday': request.POST.get('sunday') == 'on',
            }
        
        plan = StudyPlan.objects.create(
            user=request.user,
            title=title,
            description=description,
            subject=subject,
            start_date=start_datetime,
            end_date=end_datetime,
            priority=priority,
            estimated_hours=estimated_hours,
            is_recurring=is_recurring,
            recurring_pattern=recurring_pattern,
        )
        
        messages.success(request, f'Study plan "{title}" created successfully!')
        return redirect('study-planner')
    
    return render(request, 'base/create_study_plan.html')

@login_required
def edit_study_plan(request, plan_id):
    """Edit a study plan"""
    plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
    
    if request.method == 'POST':
        plan.title = request.POST.get('title')
        plan.description = request.POST.get('description')
        plan.subject = request.POST.get('subject')
        
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('end_date')
        end_time = request.POST.get('end_time')
        
        plan.start_date = timezone.make_aware(
            datetime.strptime(f"{start_date} {start_time}", '%Y-%m-%d %H:%M')
        )
        plan.end_date = timezone.make_aware(
            datetime.strptime(f"{end_date} {end_time}", '%Y-%m-%d %H:%M')
        )
        
        plan.priority = request.POST.get('priority')
        plan.estimated_hours = request.POST.get('estimated_hours')
        plan.status = request.POST.get('status')
        
        plan.save()
        messages.success(request, 'Plan updated successfully!')
        return redirect('study-planner')
    
    return render(request, 'base/edit_study_plan.html', {'plan': plan})

@login_required
def delete_study_plan(request, plan_id):
    """Delete a study plan"""
    plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
    
    if request.method == 'POST':
        plan.delete()
        messages.success(request, 'Plan deleted successfully!')
        return JsonResponse({'success': True})
    
    return render(request, 'base/delete_study_plan.html', {'plan': plan})

@login_required
def update_plan_status(request, plan_id):
    """Update plan status (mark as complete/in progress)"""
    if request.method == 'POST':
        plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
        status = request.POST.get('status')
        actual_hours = request.POST.get('actual_hours', 0)
        
        plan.status = status
        if actual_hours:
            plan.actual_hours = float(actual_hours)
        plan.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def start_study_session(request, plan_id=None):
    """Start a study session (timer)"""
    if request.method == 'POST':
        subject = request.POST.get('subject')
        plan = None
        
        if plan_id:
            plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
            subject = plan.subject
        
        session = StudySession.objects.create(
            user=request.user,
            plan=plan,
            subject=subject,
            start_time=timezone.now()
        )
        
        return JsonResponse({
            'success': True,
            'session_id': session.id,
            'start_time': session.start_time.isoformat()
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def end_study_session(request, session_id):
    """End a study session and record duration"""
    if request.method == 'POST':
        session = get_object_or_404(StudySession, id=session_id, user=request.user)
        
        session.end_time = timezone.now()
        duration = (session.end_time - session.start_time).total_seconds() / 60
        session.duration = int(duration)
        session.save()
        
        # Update plan's actual hours if linked
        if session.plan:
            session.plan.actual_hours += duration / 60
            session.plan.save()
        
        return JsonResponse({
            'success': True,
            'duration': session.duration
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def calendar_data(request):
    """Get calendar data for full calendar display"""
    user = request.user
    start = request.GET.get('start')
    end = request.GET.get('end')
    
    if start and end:
        start_date = datetime.fromisoformat(start)
        end_date = datetime.fromisoformat(end)
        
        plans = StudyPlan.objects.filter(
            user=user,
            start_date__gte=start_date,
            end_date__lte=end_date
        )
        
        events = []
        for plan in plans:
            events.append({
                'id': plan.id,
                'title': f"{plan.title} ({plan.subject})",
                'start': plan.start_date.isoformat(),
                'end': plan.end_date.isoformat(),
                'color': '#71c6dd' if plan.status == 'pending' else '#4caf50' if plan.status == 'completed' else '#ff9800',
                'url': f'/study-plan/{plan.id}/',
            })
        
        return JsonResponse(events, safe=False)
    
    return JsonResponse([], safe=False)


@login_required


def api_today_plans(request):
    """API endpoint for today's plans"""
    if not request.user.is_authenticated:
        return JsonResponse({'plans': []})
    
    today = timezone.now().date()
    plans = StudyPlan.objects.filter(
        user=request.user,
        start_date__date=today,
        status='pending'
    ).order_by('start_date')
    
    plans_data = []
    for plan in plans:
        plans_data.append({
            'id': plan.id,
            'title': plan.title,
            'subject': plan.subject,
            'start_time': plan.start_date.strftime('%I:%M %p'),
            'end_time': plan.end_date.strftime('%I:%M %p'),
        })
    
    return JsonResponse({'plans': plans_data})

def api_weekly_stats(request):
    """API endpoint for weekly stats"""
    if not request.user.is_authenticated:
        return JsonResponse({'total_hours': 0, 'total_plans': 0})
    
    # Get start of week (Monday)
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Get completed plans this week
    completed_plans = StudyPlan.objects.filter(
        user=request.user,
        status='completed',
        end_date__date__gte=start_of_week,
        end_date__date__lte=end_of_week
    )
    
    total_hours = 0
    for plan in completed_plans:
        duration = plan.end_date - plan.start_date
        total_hours += duration.total_seconds() / 3600
    
    return JsonResponse({
        'total_hours': round(total_hours, 1),
        'total_plans': completed_plans.count()
    })

def api_study_stats(request):
    """API endpoint for study stats"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'today_minutes': 0,
            'week_minutes': 0,
            'plans_today': 0,
            'upcoming_count': 0,
            'total_hours': 0,
            'completed_plans': 0,
            'current_streak': 0
        })
    
    today = timezone.now().date()
    
    # Today's study time
    today_plans = StudyPlan.objects.filter(
        user=request.user,
        start_date__date=today,
        status='completed'
    )
    today_minutes = 0
    for plan in today_plans:
        duration = plan.end_date - plan.start_date
        today_minutes += duration.total_seconds() / 60
    
    # This week's study time
    start_of_week = today - timedelta(days=today.weekday())
    week_plans = StudyPlan.objects.filter(
        user=request.user,
        status='completed',
        end_date__date__gte=start_of_week
    )
    week_minutes = 0
    for plan in week_plans:
        duration = plan.end_date - plan.start_date
        week_minutes += duration.total_seconds() / 60
    
    # Counts
    plans_today = StudyPlan.objects.filter(
        user=request.user,
        start_date__date=today
    ).count()
    
    upcoming_count = StudyPlan.objects.filter(
        user=request.user,
        start_date__gt=timezone.now(),
        status='pending'
    ).count()
    
    # Calculate streak (simplified)
    current_streak = 0
    check_date = today
    while True:
        has_plan = StudyPlan.objects.filter(
            user=request.user,
            status='completed',
            end_date__date=check_date
        ).exists()
        if has_plan:
            current_streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    return JsonResponse({
        'today_minutes': round(today_minutes),
        'week_minutes': round(week_minutes),
        'plans_today': plans_today,
        'upcoming_count': upcoming_count,
        'total_hours': round(week_minutes / 60, 1),
        'completed_plans': week_plans.count(),
        'current_streak': current_streak
    })

def check_plan_reminders(request):
    """Check and send reminders for upcoming plans"""
    if not request.user.is_authenticated:
        return JsonResponse({'reminders_sent': []})
    
    now = timezone.now()
    reminders_sent = []
    
    # Find plans starting in the next hour with reminders
    plans = StudyPlan.objects.filter(
        user=request.user,
        start_date__gt=now,
        start_date__lt=now + timedelta(hours=1),
        reminder__gt=0,
        notification_sent=False
    )
    
    for plan in plans:
        reminder_minutes = plan.reminder
        notification_time = plan.start_date - timedelta(minutes=reminder_minutes)
        
        # If it's time to send (within 1 minute of target)
        if abs((notification_time - now).total_seconds()) < 60:
            reminders_sent.append({
                'id': plan.id,
                'title': plan.title,
                'time': plan.start_date.strftime('%I:%M %p')
            })
            plan.notification_sent = True
            plan.save()
    
    return JsonResponse({'reminders_sent': reminders_sent})

def mark_plan_complete(request, plan_id):
    """Mark a study plan as complete"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    try:
        plan = StudyPlan.objects.get(id=plan_id, user=request.user)
        plan.status = 'completed'
        plan.save()
        return JsonResponse({'success': True})
    except StudyPlan.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Plan not found'})