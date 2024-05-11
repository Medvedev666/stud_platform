from course.models import Notification


def notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(for_user=request.user).filter(is_viewed=False)
    else:
        notifications = None
    return {'notifications': notifications}