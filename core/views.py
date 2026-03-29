from django.shortcuts import render
from projects.models import Project
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce


def home(request):
    # Latest projects — download count ke saath
    latest_projects = Project.objects.filter(is_active=True)\
        .annotate(total_downloads=Coalesce(Sum('downloads__download_count'), Value(0)))\
        .order_by('-created_at')[:8]

    # Trending projects — most downloaded
    trending_projects = Project.objects.filter(is_active=True)\
        .annotate(total_downloads=Coalesce(Sum('downloads__download_count'), Value(0)))\
        .order_by('-total_downloads')[:4]

    return render(request, 'core/home.html', {
        'projects': latest_projects,
        'trending_projects': trending_projects
    })


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    return render(request, 'core/contact.html')


def terms(request):
    return render(request, 'core/terms.html')


def privacy(request):
    return render(request, 'core/privacy.html')


# ================= ERROR PAGES =================
def custom_404(request, exception):
    return render(request, '404.html', status=404)


def custom_403(request, exception):
    return render(request, '403.html', status=403)


def custom_500(request):
    return render(request, '500.html', status=500)