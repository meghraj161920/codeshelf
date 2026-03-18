from django.shortcuts import render

def reviews(request):
    return render(request, 'core/home.html')  # temporary