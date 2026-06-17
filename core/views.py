from django.shortcuts import render
from projects.models import Project
from courses.models import Course
from django.contrib.auth.models import User
from django.db.models import Sum, Value, Count
from django.db.models.functions import Coalesce, Length
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from reviews.models import Review
from .models import PlatformTestimonial
import random


def home(request):
    # Latest projects — download count ke saath
    latest_projects = Project.objects.filter(is_active=True)\
        .annotate(total_downloads=Coalesce(Sum('downloads__download_count'), Value(0)))\
        .order_by('-created_at')[:8]

    # Trending projects — most downloaded
    trending_projects = Project.objects.filter(is_active=True)\
        .annotate(total_downloads=Coalesce(Sum('downloads__download_count'), Value(0)))\
        .order_by('-total_downloads')[:4]

    # Trending courses — most ordered
    trending_courses = Course.objects.filter(is_active=True)\
        .annotate(order_count=Count('order_items'))\
        .order_by('-order_count')[:4]

    # Top Sellers — highest total downloads across their projects
    top_sellers = User.objects.filter(profile__role='seller')\
        .annotate(total_downloads=Coalesce(Sum('projects__downloads__download_count'), Value(0)))\
        .order_by('-total_downloads')[:4]

    # Dynamic Stats
    projects_count = Project.objects.filter(is_active=True).count()
    courses_count = Course.objects.filter(is_active=True).count()
    downloads_count = Project.objects.filter(is_active=True).aggregate(total=Sum('downloads__download_count'))['total'] or 0
    users_count = User.objects.filter(is_active=True).count()

    context = {
        'projects': latest_projects,
        'trending_projects': trending_projects,
        'trending_courses': trending_courses,
        'top_sellers': top_sellers,
        'projects_count': projects_count,
        'courses_count': courses_count,
        'downloads_count': downloads_count,
        'users_count': users_count,
    }

    if request.user.is_authenticated and request.user.profile.role == 'seller':
        seller_testimonials = PlatformTestimonial.objects.filter(is_featured=True, user__profile__role='seller').order_by('?')[:3]
        testimonials_list = []
        for t in seller_testimonials:
            testimonials_list.append({
                'user': t.user,
                'rating': t.rating,
                'content': t.content,
                'type': 'Seller Testimonial',
                'stars': range(t.rating)
            })
        context['testimonials'] = testimonials_list
        context['is_seller_home'] = True
    else:
        # Fetch top project/course reviews
        source_a_reviews = Review.objects.annotate(text_len=Length('review_text')).filter(rating__gte=4, text_len__gt=50).order_by('?')[:3]
        
        # Fetch platform testimonials
        source_b_testimonials = PlatformTestimonial.objects.filter(is_featured=True).order_by('?')[:3]

        testimonials_list = []
        for r in source_a_reviews:
            testimonials_list.append({
                'user': r.user,
                'rating': r.rating,
                'content': r.review_text,
                'type': 'Review',
                'stars': range(r.rating)
            })
        for t in source_b_testimonials:
            testimonials_list.append({
                'user': t.user,
                'rating': t.rating,
                'content': t.content,
                'type': 'Testimonial',
                'stars': range(t.rating)
            })
        
        random.shuffle(testimonials_list)
        context['testimonials'] = testimonials_list[:3]
        context['is_seller_home'] = False

    return render(request, 'core/home.html', context)

@login_required
def submit_testimonial(request):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        rating = request.POST.get('rating')
        if content and rating:
            try:
                rating = int(rating)
                PlatformTestimonial.objects.create(
                    user=request.user,
                    content=content,
                    rating=rating,
                    is_featured=False
                )
                messages.success(request, "Thank you for your feedback! It will be reviewed by our team.")
            except ValueError:
                messages.error(request, "Invalid rating value.")
        else:
            messages.error(request, "Please provide both a rating and your feedback.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    return render(request, 'core/contact.html')


def terms(request):
    return render(request, 'core/terms.html')


def privacy(request):
    return render(request, 'core/privacy.html')

def faq(request):
    return render(request, 'core/faq.html')

def refund_policy(request):
    from django.utils.timezone import now
    return render(request, 'core/refund_policy.html', {'now': now()})


# ================= ERROR PAGES =================
def custom_404(request, exception):
    return render(request, '404.html', status=404)


def custom_403(request, exception):
    return render(request, '403.html', status=403)


def custom_500(request):
    return render(request, '500.html', status=500)


# ================= GLOBAL SEARCH =================
from django.urls import reverse

def global_search(request):
    q = request.GET.get('q', '').strip().lower()
    if not q:
        return render(request, 'core/search_results.html', {'projects': [], 'courses': [], 'pages': []})

    # Search Projects
    projects = Project.objects.filter(is_active=True, title__icontains=q)[:5]
    
    # Search Courses
    courses = Course.objects.filter(is_active=True, title__icontains=q)[:5]

    # Static Pages/Settings
    static_pages = [
        {'title': 'Home', 'url': reverse('home'), 'icon': 'fa-house'},
        {'title': 'About Us', 'url': reverse('about'), 'icon': 'fa-info-circle'},
        {'title': 'Contact', 'url': reverse('contact'), 'icon': 'fa-envelope'},
        {'title': 'All Projects', 'url': reverse('project_list'), 'icon': 'fa-code'},
        {'title': 'All Courses', 'url': reverse('course_list'), 'icon': 'fa-graduation-cap'},
    ]
    
    if request.user.is_authenticated:
        static_pages.extend([
            {'title': 'My Profile', 'url': reverse('profile'), 'icon': 'fa-user'},
            {'title': 'My Orders', 'url': reverse('order_history'), 'icon': 'fa-box'},
            {'title': 'My Coupons', 'url': reverse('coupons'), 'icon': 'fa-ticket'},
            {'title': 'Wishlist', 'url': reverse('wishlist'), 'icon': 'fa-heart'},
            {'title': 'Cart', 'url': reverse('cart'), 'icon': 'fa-cart-shopping'},
            {'title': 'Payments Dashboard', 'url': '/accounts/payments/', 'icon': 'fa-credit-card'},
        ])
        
        if hasattr(request.user, 'profile') and request.user.profile.role == 'seller':
            static_pages.extend([
                {'title': 'Seller Dashboard', 'url': reverse('seller_dashboard'), 'icon': 'fa-chart-line'},
                {'title': 'Upload Project', 'url': reverse('upload_project'), 'icon': 'fa-upload'},
            ])
        else:
            static_pages.extend([
                {'title': 'Customer Dashboard', 'url': reverse('customer_dashboard'), 'icon': 'fa-table-cells-large'},
            ])
    else:
        static_pages.extend([
            {'title': 'Login', 'url': reverse('login'), 'icon': 'fa-right-to-bracket'},
            {'title': 'Sign Up', 'url': reverse('register'), 'icon': 'fa-user-plus'},
        ])

    matched_pages = [p for p in static_pages if q in p['title'].lower()][:5]

    return render(request, 'core/search_results.html', {
        'projects': projects,
        'courses': courses,
        'pages': matched_pages,
        'query': q,
    })


# ================= NEWSLETTER =================
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import NewsletterSubscriber

@require_POST
def subscribe_newsletter(request):
    email = request.POST.get('email', '').strip()
    
    if not email:
        return JsonResponse({'status': 'error', 'message': 'Email address is required.'})
    
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Please provide a valid email address.'})
        
    subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
    
    if created:
        return JsonResponse({'status': 'success', 'message': 'Thank you for subscribing to our newsletter!'})
    else:
        if not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save()
            return JsonResponse({'status': 'success', 'message': 'Welcome back! You have been re-subscribed.'})
        else:
            return JsonResponse({'status': 'info', 'message': 'You are already subscribed!'})