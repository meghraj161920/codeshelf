from django.shortcuts import render, get_object_or_404
from .models import Project, Category


def project_list(request):
    projects = Project.objects.filter(is_active=True)
    categories = Category.objects.all()

    # GET parameters
    category = request.GET.get('category')
    technology = request.GET.get('technology')
    difficulty = request.GET.get('difficulty')
    search = request.GET.get('q')

    # FILTERS
    if category:
        projects = projects.filter(category__slug=category)

    if technology:
        projects = projects.filter(technology__icontains=technology)

    if difficulty:
        projects = projects.filter(difficulty_level=difficulty)

    if search:
        projects = projects.filter(title__icontains=search)

    context = {
        'projects': projects,
        'categories': categories
    }

    return render(request, 'projects/project_list.html', context)


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, is_active=True)

    context = {
        'project': project
    }

    return render(request, 'projects/project_detail.html', context)