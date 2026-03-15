from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

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
    path('favicon.ico', RedirectView.as_view(url='/static/images/avatar.svg', permanent=True)),
    path('assets/favicon.ico', RedirectView.as_view(url='/static/images/avatar.svg', permanent=True)),
    path('about-us/', views.about_us, name='about-us'),
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),
    path('terms-of-service/', views.terms_of_service, name='terms-of-service'),
    path('help-center/', views.help_center, name='help-center'),
    path('debug-brevo/', views.debug_brevo_api, name='debug-brevo'),
    path('study-planner/', views.study_planner, name='study-planner'),
path('create-study-plan/', views.create_study_plan, name='create-study-plan'),
path('edit-study-plan/<int:plan_id>/', views.edit_study_plan, name='edit-study-plan'),
path('delete-study-plan/<int:plan_id>/', views.delete_study_plan, name='delete-study-plan'),
path('update-plan-status/<int:plan_id>/', views.update_plan_status, name='update-plan-status'),
path('start-study-session/<int:plan_id>/', views.start_study_session, name='start-study-session'),
path('end-study-session/<int:session_id>/', views.end_study_session, name='end-study-session'),
path('calendar-data/', views.calendar_data, name='calendar-data'),
path('api/today-plans/', views.api_today_plans, name='api-today-plans'),

    path('api/weekly-stats/', views.api_weekly_stats, name='api-weekly-stats'),
    path('api/study-stats/', views.api_study_stats, name='api-study-stats'),
    path('check-plan-reminders/', views.check_plan_reminders, name='check-plan-reminders'),
    path('mark-plan-complete/<int:plan_id>/', views.mark_plan_complete, name='mark-plan-complete'),
]
