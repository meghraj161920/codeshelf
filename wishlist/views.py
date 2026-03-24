from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Wishlist
from projects.models import Project

def wishlist(request):
    return render(request, 'wishlist/wishlist.html')

@login_required
def toggle_wishlist(request):
    if request.method == "POST":
        project_id = request.POST.get("project_id")
        project = Project.objects.get(id=project_id)

        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            project=project
        )

        if not created:
            wishlist_item.delete()
            return JsonResponse({"status": "removed"})

        return JsonResponse({"status": "added"})