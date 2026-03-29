from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Wishlist
from projects.models import Project


# ================= WISHLIST VIEW =================
@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related('project')
    return render(request, 'wishlist/wishlist.html', {'items': items})


# ================= TOGGLE WISHLIST =================
@login_required
def toggle_wishlist(request):
    if request.method == "POST":
        project_id = request.POST.get("project_id")
        project = get_object_or_404(Project, id=project_id)

        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            project=project
        )

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