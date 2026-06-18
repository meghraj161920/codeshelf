from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Course, CourseCategory, CourseVideo
from .forms import CourseUploadForm
from core.decorators import seller_required
from orders.models import OrderItem


def course_list(request):
    """
    Shows all active courses.
    Supports filtering by category slug and difficulty level.
    Supports search by course title.
    Auto-submit filters on change (handled in template).
    """
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'seller':
        courses = Course.objects.filter(seller=request.user)
    else:
        courses = Course.objects.filter(is_active=True)
    categories = CourseCategory.objects.all()

    category = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    pricing = request.GET.get('pricing')
    search = request.GET.get('q')

    if category:
        courses = courses.filter(category__slug=category)
    if difficulty:
        courses = courses.filter(difficulty_level=difficulty)
    if pricing:
        if pricing == 'free':
            courses = courses.filter(is_free=True)
        elif pricing == 'paid':
            courses = courses.filter(is_free=False)
    if search:
        courses = courses.filter(title__icontains=search)

    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    page_range = paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)

    return render(request, 'courses/course_list.html', {
        'courses': page_obj,
        'page_range': page_range,
        'categories': categories,
    })


def course_detail(request, slug):
    """
    Shows course detail page with full video list on left
    and YouTube player on right (Udemy style).
    Gets selected video from URL parameter ?video=ID.
    Defaults to first video if no parameter is given.
    """
    course = get_object_or_404(Course, slug=slug)
    videos = course.videos.all().order_by('order')

    video_id = request.GET.get('video')
    if video_id:
        current_video = get_object_or_404(CourseVideo, id=video_id, course=course)
    else:
        current_video = videos.first()

    has_purchased = False
    is_expired = False
    if request.user.is_authenticated:
        order_item = OrderItem.objects.filter(
            order__user=request.user,
            order__is_completed=True,
            course=course
        ).order_by('-order__order_date').first()

        if order_item:
            has_purchased = True
            if course.access_duration_months > 0:
                from datetime import timedelta
                from django.utils.timezone import now
                expiration_date = order_item.order.order_date + timedelta(days=30 * course.access_duration_months)
                if now() > expiration_date:
                    is_expired = True
                    has_purchased = False

    if not course.is_active:
        is_seller = request.user.is_authenticated and course.seller == request.user
        if not (is_seller or has_purchased):
            from django.http import Http404
            raise Http404("No active Course matches the given query.")

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'videos': videos,
        'current_video': current_video,
        'has_purchased': has_purchased,
        'is_expired': is_expired,
    })


@seller_required
def upload_course(request):
    if request.method == "POST":
        form = CourseUploadForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.seller = request.user
            course.save()
            messages.success(request, "Course uploaded successfully!")
            return redirect('seller_dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = CourseUploadForm()

    return render(request, 'courses/upload_course.html', {'form': form})
