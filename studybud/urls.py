from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include
from django.http import FileResponse
import os
from django.conf import settings
from django.http import HttpResponseNotFound

def serve_onesignal_worker(request, filename):
    """Serve OneSignal worker files from root"""
    file_path = os.path.join(settings.BASE_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/javascript')
    return HttpResponseNotFound()



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
    path('api/', include('base.api.urls')),
    path('password-reset/', 
     auth_views.PasswordResetView.as_view(template_name='base/password_reset.html'), 
     name='password_reset'),
    path('password-reset/done/', 
     auth_views.PasswordResetDoneView.as_view(template_name='base/password_reset_done.html'), 
     name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
     auth_views.PasswordResetConfirmView.as_view(template_name='base/password_reset_confirm.html'), 
     name='password_reset_confirm'),
    path('reset/done/', 
     auth_views.PasswordResetCompleteView.as_view(template_name='base/password_reset_complete.html'), 
     name='password_reset_complete'),
     path('admin/', admin.site.urls),
    path('', include('base.urls')),
    # Serve OneSignal worker files
    path('OneSignalSDKWorker.js', serve_onesignal_worker, {'filename': 'OneSignalSDKWorker.js'}),
    path('OneSignalSDK.sw.js', serve_onesignal_worker, {'filename': 'OneSignalSDK.sw.js'}),

]
