from .models import Notification

def notification_count(request):
    if request.user.is_authenticated:
        notifications = request.user.notifications.filter(is_read=False)
        return {
            'notifications': notifications,
            'notification_count': notifications.count()
        }
    return {}
