from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Wishlist
from projects.models import Project
from courses.models import Course


# ================= WISHLIST VIEW =================
@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related('project', 'course')
    
    from orders.models import OrderItem
    purchased_course_ids = OrderItem.objects.filter(
        order__user=request.user,
        order__is_completed=True,
        course__isnull=False
    ).values_list('course_id', flat=True)

    purchased_project_ids = OrderItem.objects.filter(
        order__user=request.user,
        order__is_completed=True,
        project__isnull=False
    ).values_list('project_id', flat=True)

    return render(request, 'wishlist/wishlist.html', {
        'items': items,
        'purchased_course_ids': list(purchased_course_ids),
        'purchased_project_ids': list(purchased_project_ids)
    })


# ================= TOGGLE WISHLIST =================
@login_required
def toggle_wishlist(request):
    if request.method == "POST":
        item_type = request.POST.get("item_type")
        item_id = request.POST.get("item_id")
        
        # Fallback for old requests that just sent project_id
        if not item_type and not item_id:
            item_id = request.POST.get("project_id")
            item_type = 'project'

        if not item_id or not item_type:
            return JsonResponse({'error': 'Missing parameters'}, status=400)

        if item_type == 'project':
            item = get_object_or_404(Project, id=item_id)
            wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, project=item)
        elif item_type == 'course':
            item = get_object_or_404(Course, id=item_id)
            wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, course=item)
        else:
            return JsonResponse({'error': 'Invalid item type'}, status=400)

        if not created:
            wishlist_item.delete()
            status = 'removed'
        else:
            status = 'added'

        return JsonResponse({
            'status': status,
            'wishlist_count': Wishlist.objects.filter(user=request.user).count()
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)