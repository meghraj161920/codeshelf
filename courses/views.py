from django.shortcuts import render, get_object_or_404
from .models import Course, CourseCategory, CourseVideo


def course_list(request):
    """
    Shows all active courses.
    Supports filtering by category slug and difficulty level.
    Supports search by course title.
    Auto-submit filters on change (handled in template).
    """
    courses = Course.objects.filter(is_active=True)
    categories = CourseCategory.objects.all()

    category = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    search = request.GET.get('q')

    if category:
        courses = courses.filter(category__slug=category)
    if difficulty:
        courses = courses.filter(difficulty_level=difficulty)
    if search:
        courses = courses.filter(title__icontains=search)

    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'categories': categories,
    })


def course_detail(request, slug):
    """
    Shows course detail page with full video list on left
    and YouTube player on right (Udemy style).
    Gets selected video from URL parameter ?video=ID.
    Defaults to first video if no parameter is given.
    """
    course = get_object_or_404(Course, slug=slug, is_active=True)
    videos = course.videos.all().order_by('order')

    video_id = request.GET.get('video')
    if video_id:
        current_video = get_object_or_404(CourseVideo, id=video_id, course=course)
    else:
        current_video = videos.first()

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'videos': videos,
        'current_video': current_video,
    })
