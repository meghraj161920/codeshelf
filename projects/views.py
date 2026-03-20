from django.shortcuts import render, get_object_or_404
from .models import Project, Category


def project_list(request):
    projects = Project.objects.filter(is_active=True)
    categories = Category.objects.all()

    category = request.GET.get('category')

    if category:
        projects = projects.filter(category__slug=category)

    context = {
        'projects': projects,
        'categories': categories
    }

    return render(request, 'projects/project_list.html', context)


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)

    context = {
        'project': project
    }

    return render(request, 'projects/project_detail.html', context)