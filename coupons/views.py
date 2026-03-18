from pyexpat.errors import messages
from django.shortcuts import redirect, render


def coupons(request):
    return render(request, 'accounts/coupons.html')


def apply_coupon(request):

    context = {
        "message": "Coupon REVIEW10 applied successfully!"
    }

    return render(request, "coupons/apply_coupon.html", context)
