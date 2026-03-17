from django.shortcuts import render

def project_list(request):
    return render(request, 'projects/project_list.html')