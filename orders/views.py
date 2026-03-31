from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from projects.models import Project
from coupons.models import Coupon, UserCoupon


# ================= CHECKOUT =================
@login_required
def checkout(request):
    cart = request.session.get('cart', [])

    if not cart:
        messages.error(request, "Your cart is empty!")
        return redirect('cart')

    projects = Project.objects.filter(id__in=cart)
    subtotal = sum(p.price for p in projects)

    # Coupon discount
    discount = 0
    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            discount = (subtotal * coupon.discount_percent) / 100
        except Coupon.DoesNotExist:
            request.session.pop('coupon_code', None)

    total = subtotal - discount

    return render(request, "orders/checkout.html", {
        "projects": projects,
        "subtotal": subtotal,
        "discount": discount,
        "total": total,
        "coupon_code": coupon_code,
    })


# ================= APPLY COUPON =================
@login_required
def apply_coupon(request):
    if request.method == "POST":
        code = request.POST.get("coupon_code", "").strip().upper()

        try:
            coupon = Coupon.objects.get(code=code, is_active=True)

            # Check if user has this coupon
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


# ================= PLACE ORDER =================
@login_required
def place_order(request):
    if request.method == "POST":
        cart = request.session.get('cart', [])

        if not cart:
            messages.error(request, "Your cart is empty!")
            return redirect('cart')

        projects = Project.objects.filter(id__in=cart)

        # ✅ Filter out already purchased projects
        already_purchased = []
        valid_projects = []

        for project in projects:
            purchased = OrderItem.objects.filter(
                order__user=request.user,
                order__is_completed=True,
                project=project
            ).exists()

            if purchased:
                already_purchased.append(project.title)
            else:
                valid_projects.append(project)

        # ✅ If all projects already purchased
        if not valid_projects:
            messages.error(request, "You have already purchased all projects in your cart.")
            request.session['cart'] = []
            return redirect('cart')

        # ✅ Warn about some already purchased
        if already_purchased:
            messages.warning(request, f"Skipped already purchased: {', '.join(already_purchased)}")

        subtotal = sum(p.price for p in valid_projects)

        # Coupon discount
        discount = 0
        coupon_obj = None
        coupon_code = request.session.get('coupon_code')
        if coupon_code:
            try:
                coupon_obj = Coupon.objects.get(code=coupon_code, is_active=True)
                discount = (subtotal * coupon_obj.discount_percent) / 100
            except Coupon.DoesNotExist:
                pass

        total = subtotal - discount
        payment_method = request.POST.get('payment_method', 'upi')

        # Create Order
        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            payment_method=payment_method,
            payment_status='completed',
            is_completed=True
        )

        # Create OrderItems for valid projects only
        for project in valid_projects:
            OrderItem.objects.create(
                order=order,
                project=project,
                price=project.price
            )

        # Mark coupon as used
        if coupon_obj:
            UserCoupon.objects.filter(
                user=request.user,
                coupon=coupon_obj
            ).update(is_used=True)
            request.session.pop('coupon_code', None)

        # Clear cart
        request.session['cart'] = []

        return redirect('order_success', order_id=order.id)

    return redirect('checkout')


# ================= ORDER SUCCESS =================
@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/order_success.html", {"order": order})


# ================= ORDER HISTORY =================
@login_required
def order_history(request):
    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related('items__project').order_by('-order_date')

    return render(request, "orders/order_history.html", {"orders": orders})