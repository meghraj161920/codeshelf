from projects.models import Project
from django.contrib.auth import get_user_model

User = get_user_model()

def footer_stats(request):
    try:
        total_projects = Project.objects.filter(is_active=True).count()
        total_users = User.objects.filter(is_active=True).count()
        total_sellers = User.objects.filter(profile__role='seller', is_active=True).count()
    except Exception:
        total_projects = 0
        total_users = 0
        total_sellers = 0

    return {
        'footer_total_projects': total_projects,
        'footer_total_users': total_users,
        'footer_total_sellers': total_sellers,
    }
