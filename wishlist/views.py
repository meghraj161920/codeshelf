from django.shortcuts import render

def wishlist(request):
    return render(request, 'accounts/wishlist.html')