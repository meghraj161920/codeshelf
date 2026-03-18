from django.shortcuts import render

def orders(request):
    return render(request, 'accounts/my_purchases.html')