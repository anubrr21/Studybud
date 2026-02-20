from django.urls import path
from  .import views
urlpatterns=[
    path('login/',views.loginPage,name="login"),
    path('logout/',views.logoutUser,name="logout"),
    path('register/',views.registerPage,name="register"),
    path('',views.home ,name="home"),
    path('room/<str:pk>/',views.room,name="room"),
    path('profile/<str:pk>/',views.userProfile,name="user-profile"),
    path('create-room/',views.createRoom,name="create-room"),
    path('update-room/<str:pk>/',views.updateRoom,name="update-room"),
    path('delete-room/<str:pk>/',views.deleteRoom,name="delete-room"),
    path('delete-message/<str:pk>/',views.deleteMessage,name="delete-message"),
    path('update-user/',views.updateUser,name="update-user"),
    path('topics/',views.topicsPage,name="topics"),
    path('activity/',views.activityPage,name="activity"),
    path('like-room/<str:pk>/', views.toggle_like, name="toggle-like"),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read/', views.mark_notifications_read, name='mark-notifications-read'),
    path('follow/<int:pk>/', views.toggle_follow, name='toggle-follow'),
    path('profile-followers/<int:pk>/', views.profile_followers, name='profile-followers'),
    path('profile-following/<int:pk>/', views.profile_following, name='profile-following'),


]