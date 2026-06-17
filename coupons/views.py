from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Coupon, UserCoupon
from .utils import is_coupon_valid


# ================= MY COUPONS =================
@login_required
def coupons(request):
    user_coupons = UserCoupon.objects.filter(
        user=request.user
    ).select_related('coupon').order_by('-created_at')

    all_global_coupons = Coupon.objects.filter(is_active=True, is_global=True).order_by('-discount_percent')
    used_coupons = UserCoupon.objects.filter(user=request.user, is_used=True).values_list('coupon_id', flat=True)
    all_global_coupons = all_global_coupons.exclude(id__in=used_coupons)
    
    valid_global_coupons = []
    for c in all_global_coupons:
        # Pass cart_items_count=2 so COMBO15 can be displayed
        valid, _ = is_coupon_valid(c.code, request.user, cart_items_count=2)
        if valid:
            valid_global_coupons.append(c)

    return render(request, 'coupons/coupons.html', {
        'user_coupons': user_coupons,
        'global_coupons': valid_global_coupons,
    })


# ================= APPLY COUPON =================
@login_required
def apply_coupon(request):
    if request.method == "POST":
        code = request.POST.get("coupon_code", "").strip().upper()

        try:
            coupon = Coupon.objects.get(code=code, is_active=True)

            if coupon.is_global:
                from orders.views import get_cart_dict
                cart = get_cart_dict(request)
                cart_items_count = len(cart['projects']) + len(cart['courses'])
                valid, err_msg = is_coupon_valid(coupon.code, request.user, cart_items_count)
                if not valid:
                    messages.error(request, err_msg)
                    return redirect('checkout')
            else:
                user_coupon = UserCoupon.objects.filter(
                    user=request.user,
                    coupon=coupon,
                    is_used=False
                ).first()

                if not user_coupon:
                    messages.error(request, "You don't have this coupon or it's already used.")
                    return redirect('checkout')

            request.session['coupon_code'] = code
            messages.success(request, f"Coupon applied! {coupon.discount_percent}% discount.")

        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")

    return redirect('checkout')