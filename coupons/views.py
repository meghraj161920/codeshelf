from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Coupon, UserCoupon


# ================= MY COUPONS =================
@login_required
def coupons(request):
    user_coupons = UserCoupon.objects.filter(
        user=request.user
    ).select_related('coupon').order_by('-created_at')

    return render(request, 'coupons/coupons.html', {
        'user_coupons': user_coupons
    })


# ================= APPLY COUPON =================
@login_required
def apply_coupon(request):
    if request.method == "POST":
        code = request.POST.get("coupon_code", "").strip().upper()

        try:
            coupon = Coupon.objects.get(code=code, is_active=True)

            # User ke paas yeh coupon hai?
            user_coupon = UserCoupon.objects.filter(
                user=request.user,
                coupon=coupon,
                is_used=False
            ).first()

            if not user_coupon:
                messages.error(request, "You don't have this coupon or it's already used.")
            else:
                request.session['coupon_code'] = code
                messages.success(request, f"Coupon applied! {coupon.discount_percent}% discount.")

        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")

    return redirect('checkout')