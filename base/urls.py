from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),
    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),
    path('update-user/', views.updateUser, name="update-user"),
    path('topics/', views.topicsPage, name="topics"),
    path('activity/', views.activityPage, name="activity"),
    path('like-room/<str:pk>/', views.toggle_like, name="toggle-like"),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read/', views.mark_notifications_read, name='mark-notifications-read'),
    path('follow/<int:pk>/', views.toggle_follow, name='toggle-follow'),
    path('profile-followers/<int:pk>/', views.profile_followers, name='profile-followers'),
    path('profile-following/<int:pk>/', views.profile_following, name='profile-following'),
    path('edit-message/<int:pk>/', views.edit_message, name='edit-message'),
    path('delete-account/', views.delete_account, name='delete-account'),
    path('pin-message/<int:message_id>/', views.pin_message, name='pin-message'),
    path('unpin-message/<int:message_id>/', views.unpin_message, name='unpin-message'),
    path('verify-email/<int:user_id>/', views.verify_email, name='verify-email'),
    path('resend-verification/<int:user_id>/', views.resend_verification, name='resend-verification'),
    
    # Password reset URLs
  
     path('password-reset/', 
     views.CustomPasswordResetView.as_view(), 
     name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='base/password_reset_done.html'
         ), name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='base/password_reset_confirm.html'
         ), name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='base/password_reset_complete.html'
         ), name='password_reset_complete'),
    path('all-rooms/', views.all_rooms, name='all-rooms'),
    path('chats/', views.chats_list, name='chats'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat-detail'),
    path('start-chat/<int:user_id>/', views.start_chat, name='start-chat'),
    path('chat/<int:chat_id>/update-theme/', views.update_chat_theme, name='update-chat-theme'),
    path('api/search-chats/', views.search_chats, name='search-chats'),
    path('api/unread-chats-count/', views.get_unread_chats_count, name='unread-chats-count'),
    path('api/search-users/', views.search_users, name='search-users'),
    path('chat/<int:chat_id>/upload/', views.upload_chat_file, name='upload-chat-file'),
]