from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q
from coupons.utils import is_coupon_valid
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from projects.models import Project
from courses.models import Course
from coupons.models import Coupon, UserCoupon
from core.email_utils import send_order_confirmation_email
from django.core.paginator import Paginator

def get_cart_dict(request):
    cart = request.session.get('cart', {'projects': [], 'courses': []})
    if isinstance(cart, list):
        cart = {'projects': cart, 'courses': []}
        request.session['cart'] = cart
    return cart

# ================= CHECKOUT =================

@login_required
def checkout(request):
    cart = get_cart_dict(request)

    if not cart['projects'] and not cart['courses']:
        messages.error(request, "Your cart is empty!")
        return redirect('cart')

    projects = Project.objects.filter(id__in=cart['projects'])
    courses = Course.objects.filter(id__in=cart['courses'])
    
    subtotal = sum(p.price for p in projects) + sum(c.price for c in courses)

    # Coupon discount
    discount = 0
    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            has_used = UserCoupon.objects.filter(user=request.user, coupon=coupon, is_used=True).exists()
            if not has_used:
                discount = (subtotal * coupon.discount_percent) / 100
            else:
                request.session.pop('coupon_code', None)
        except Coupon.DoesNotExist:
            request.session.pop('coupon_code', None)

    total = subtotal - discount

    # Fetch all active coupons from the DB
    available_coupons = Coupon.objects.filter(is_active=True).order_by('-id')
    used_coupons = UserCoupon.objects.filter(user=request.user, is_used=True).values_list('coupon_id', flat=True)
    my_assigned_coupons = UserCoupon.objects.filter(user=request.user, is_used=False).values_list('coupon_id', flat=True)
    
    available_coupons_qs = available_coupons.filter(Q(is_global=True) | Q(id__in=my_assigned_coupons)).exclude(id__in=used_coupons)

    cart_items_count = len(projects) + len(courses)
    available_coupons = []
    for c in available_coupons_qs:
        if c.is_global:
            valid, _ = is_coupon_valid(c.code, request.user, cart_items_count)
            if valid:
                available_coupons.append(c)
        else:
            available_coupons.append(c)

    return render(request, "orders/checkout.html", {
        "projects": projects,
        "courses": courses,
        "subtotal": subtotal,
        "discount": discount,
        "total": total,
        "coupon_code": coupon_code,
        "available_coupons": available_coupons,
    })


# ================= APPLY COUPON =================
@login_required
def apply_coupon(request):
    if request.method == "POST":
        code = request.POST.get("coupon_code", "").strip().upper()
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            user_coupon_used = UserCoupon.objects.filter(user=request.user, coupon=coupon, is_used=True).exists()
            if user_coupon_used:
                messages.error(request, "You have already used this coupon.")
            else:
                if coupon.is_global:
                    cart = get_cart_dict(request)
                    cart_items_count = len(cart['projects']) + len(cart['courses'])
                    valid, err_msg = is_coupon_valid(coupon.code, request.user, cart_items_count)
                    if not valid:
                        messages.error(request, err_msg)
                        return redirect('checkout')
                else:
                    is_assigned = UserCoupon.objects.filter(user=request.user, coupon=coupon, is_used=False).exists()
                    if not is_assigned:
                        messages.error(request, "You don't have this coupon or it's already used.")
                        return redirect('checkout')

                request.session['coupon_code'] = code
                messages.success(request, f"Coupon applied! {coupon.discount_percent}% discount.")
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")
    return redirect('checkout')


# ================= PAYMENT SELECTION =================
@login_required
def payment_selection(request):
    cart = get_cart_dict(request)
    if not cart['projects'] and not cart['courses']:
        messages.error(request, "Your cart is empty!")
        return redirect('cart')

    projects = Project.objects.filter(id__in=cart['projects'])
    courses = Course.objects.filter(id__in=cart['courses'])
    subtotal = sum(p.price for p in projects) + sum(c.price for c in courses)
    
    discount = 0
    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        try:
            coupon_obj = Coupon.objects.get(code=coupon_code, is_active=True)
            has_used = UserCoupon.objects.filter(user=request.user, coupon=coupon_obj, is_used=True).exists()
            if not has_used:
                discount = (subtotal * coupon_obj.discount_percent) / 100
        except Coupon.DoesNotExist:
            pass

    total = subtotal - discount
    return render(request, "orders/payment.html", {"total": total})


# ================= PLACE ORDER =================
@login_required
def place_order(request):
    if request.method == "POST":
        cart = get_cart_dict(request)

        if not cart['projects'] and not cart['courses']:
            messages.error(request, "Your cart is empty!")
            return redirect('cart')

        projects = Project.objects.filter(id__in=cart['projects'])
        courses = Course.objects.filter(id__in=cart['courses'])

        already_purchased = []
        valid_projects = []
        valid_courses = []

        for project in projects:
            purchased = OrderItem.objects.filter(order__user=request.user, order__is_completed=True, project=project).exists()
            if purchased:
                already_purchased.append(project.title)
            else:
                valid_projects.append(project)

        for course in courses:
            purchased = OrderItem.objects.filter(order__user=request.user, order__is_completed=True, course=course).exists()
            if purchased:
                already_purchased.append(course.title)
            else:
                valid_courses.append(course)

        if not valid_projects and not valid_courses:
            messages.error(request, "You have already purchased all items in your cart.")
            request.session['cart'] = {'projects': [], 'courses': []}
            return redirect('cart')

        if already_purchased:
            messages.warning(request, f"Skipped already purchased: {', '.join(already_purchased)}")

        subtotal = sum(p.price for p in valid_projects) + sum(c.price for c in valid_courses)

        # Coupon discount check
        discount = 0
        coupon_obj = None
        coupon_code = request.session.get('coupon_code')
        if coupon_code:
            try:
                coupon_obj = Coupon.objects.get(code=coupon_code, is_active=True)
                has_used = UserCoupon.objects.filter(user=request.user, coupon=coupon_obj, is_used=True).exists()
                if not has_used:
                    if coupon_obj.is_global:
                        cart_items_count = len(valid_projects) + len(valid_courses)
                        valid, _ = is_coupon_valid(coupon_obj.code, request.user, cart_items_count)
                        if not valid:
                            coupon_obj = None
                            request.session.pop('coupon_code', None)
                    else:
                        is_assigned = UserCoupon.objects.filter(user=request.user, coupon=coupon_obj, is_used=False).exists()
                        if not is_assigned:
                            coupon_obj = None
                            request.session.pop('coupon_code', None)
                    if coupon_obj:
                        discount = (subtotal * coupon_obj.discount_percent) / 100
                else:
                    coupon_obj = None
                    request.session.pop('coupon_code', None)
            except Coupon.DoesNotExist:
                pass

        total = subtotal - discount
        payment_method = request.POST.get('payment_method', 'upi')
        additional_remarks = request.POST.get('additional_remarks', '')

        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            payment_method=payment_method,
            payment_status='completed',
            is_completed=True,
            additional_remarks=additional_remarks
        )

        from wishlist.models import Wishlist

        for project in valid_projects:
            OrderItem.objects.create(order=order, project=project, price=project.price)
            Wishlist.objects.filter(user=request.user, project=project).delete()
            
        for course in valid_courses:
            OrderItem.objects.create(order=order, course=course, price=course.price)
            # Courses are left in the wishlist to be marked as 'Already Purchased' by the template

        if coupon_obj:
            if coupon_obj.code != 'SAVE5':
                UserCoupon.objects.update_or_create(user=request.user, coupon=coupon_obj, defaults={'is_used': True})
            request.session.pop('coupon_code', None)

        send_order_confirmation_email(request.user, order)
        request.session['cart'] = {'projects': [], 'courses': []}

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
    ).prefetch_related('items__project', 'items__course').order_by('-order_date')

    purchased_projects = Project.objects.filter(
        order_items__order__user=request.user,
        order_items__order__is_completed=True
    ).distinct().order_by('-id')

    purchased_courses = Course.objects.filter(
        order_items__order__user=request.user,
        order_items__order__is_completed=True
    ).distinct().order_by('-id')

    # Pagination for Projects
    paginator_p = Paginator(purchased_projects, 4)
    page_number_p = request.GET.get('page_p')
    projects_page = paginator_p.get_page(page_number_p)

    # Pagination for Courses
    paginator_c = Paginator(purchased_courses, 4)
    page_number_c = request.GET.get('page_c')
    courses_page = paginator_c.get_page(page_number_c)

    return render(request, "orders/order_history.html", {
        "orders": orders,
        "purchased_projects": projects_page,
        "purchased_courses": courses_page,
        "page_range_p": paginator_p.get_elided_page_range(projects_page.number, on_each_side=1, on_ends=1) if paginator_p.num_pages > 1 else [],
        "page_range_c": paginator_c.get_elided_page_range(courses_page.number, on_each_side=1, on_ends=1) if paginator_c.num_pages > 1 else [],
    })
