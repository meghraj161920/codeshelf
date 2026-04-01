from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse
from django.utils import timezone
import os
from django.http import JsonResponse

from .models import Project, Category, ProjectDownload
from .forms import ProjectUploadForm
from wishlist.models import Wishlist
from orders.models import OrderItem
from core.decorators import seller_required


# ================= PROJECT LIST =================
def project_list(request):
    projects = Project.objects.filter(is_active=True)
    categories = Category.objects.all()

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(Wishlist.objects.filter(user=request.user)
                        .values_list('project_id', flat=True))

    category = request.GET.get('category')
    technology = request.GET.get('technology')
    difficulty = request.GET.get('difficulty')
    search = request.GET.get('q')

    if category:
        projects = projects.filter(category__slug=category)
    if technology:
        projects = projects.filter(technology__icontains=technology)
    if difficulty:
        projects = projects.filter(difficulty_level=difficulty)
    if search:
        projects = projects.filter(title__icontains=search)

    return render(request, 'projects/project_list.html', {
        'projects': projects,
        'categories': categories,
        'wishlist_ids': wishlist_ids,
    })


# ================= PROJECT DETAIL =================
def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, is_active=True)

    related_projects = Project.objects.filter(
        category=project.category,
        is_active=True
    ).exclude(id=project.id)[:4]

    wishlist_ids = []
    has_purchased = False  # ✅ Default False

    if request.user.is_authenticated:
        wishlist_ids = list(Wishlist.objects.filter(user=request.user)
                        .values_list('project_id', flat=True))

        # ✅ Purchase check
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            order__is_completed=True,
            project=project
        ).exists()

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'related_projects': related_projects,
        'wishlist_ids': wishlist_ids,
        'has_purchased': has_purchased,  # ✅ Template ko pass karo
    })


# ================= UPLOAD PROJECT =================
@seller_required
def upload_project(request):
    if request.method == "POST":
        form = ProjectUploadForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.seller = request.user
            project.save()
            messages.success(request, "Project uploaded successfully!")
            return redirect('seller_dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ProjectUploadForm()

    return render(request, 'projects/upload_project.html', {'form': form})


# ================= DELETE PROJECT =================
@seller_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, seller=request.user)
    project.delete()
    messages.success(request, "Project deleted successfully!")
    return redirect('seller_dashboard')


# ================= DOWNLOAD PROJECT =================
@login_required
def download_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, is_active=True)

    # ✅ Purchase check
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        order__is_completed=True,
        project=project
    ).exists()

    if not has_purchased:
        messages.error(request, "You must purchase this project before downloading.")
        return redirect('project_detail', slug=project.slug)

    # ✅ File check
    if not project.zip_file:
        messages.error(request, "File not available. Please contact support.")
        return redirect('project_detail', slug=project.slug)

    # ✅ Download count track
    download_record, created = ProjectDownload.objects.get_or_create(
        user=request.user,
        project=project
    )
    download_record.download_count += 1
    download_record.last_downloaded = timezone.now()
    download_record.save()

    # ✅ File serve
    file_path = project.zip_file.path
    if os.path.exists(file_path):
        return FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=f"{project.slug}.zip"
        )
    else:
        messages.error(request, "File not found on server.")
        return redirect('project_detail', slug=project.slug)
    
    
def search_suggestions(request):
    """
    AJAX view that returns project suggestions as JSON.
    Called every time user types in the search bar.
    Returns max 6 results matching the query.
    """
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'results': []})

    projects = Project.objects.filter(
        is_active=True,
        title__icontains=query
    ).values('title', 'slug', 'price', 'technology')[:6]

    results = list(projects)
    return JsonResponse({'results': results})
