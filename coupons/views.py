from django.shortcuts import render

def coupons(request):
    return render(request, 'accounts/coupons.html')