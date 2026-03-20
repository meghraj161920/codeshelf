from django.shortcuts import redirect, render
from django.contrib import messages


def coupons(request):
    return render(request, 'accounts/coupons.html')


def apply_coupon(request):

    if request.method == "POST":
        code = request.POST.get("coupon_code")

        if code == "REVIEW10":
            request.session["discount"] = 100
            messages.success(request, "Coupon REVIEW10 applied successfully!")
        else:
            request.session["discount"] = 0
            messages.error(request, "Invalid coupon code")

    return redirect('checkout')
