from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from projects.models import Project
from orders.models import OrderItem
from coupons.models import Coupon, UserCoupon
import random
import string
from django.utils import timezone
from core.email_utils import send_review_thank_you_email


# ================= REVIEW LIST =================
def review_list(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'reviews/review_list.html', {'reviews': reviews})


# ================= ADD REVIEW =================
@login_required
def add_review(request):
    if request.method == "POST":
        project_id = request.POST.get("project_id")
        rating = request.POST.get("rating")
        review_text = request.POST.get("comment")

        project = get_object_or_404(Project, id=project_id)

        # ✅ Check — user ne project purchase kiya hai?
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            order__is_completed=True,
            project=project
        ).exists()

        if not has_purchased:
            messages.error(
                request, "You can only review projects you have purchased.")
            return redirect('project_detail', slug=project.slug)

        # ✅ Check — user ne pehle se review diya hai?
        already_reviewed = Review.objects.filter(
            user=request.user,
            project=project
        ).exists()

        if already_reviewed:
            messages.error(request, "You have already reviewed this project.")
            return redirect('project_detail', slug=project.slug)

        # ✅ Review save karo
        review_obj = Review.objects.create(
            user=request.user,
            project=project,
            rating=int(rating),
            review_text=review_text
        )

        # ✅ Coupon generate karo
        coupon = generate_coupon_for_user(request.user)

        send_review_thank_you_email(request.user, review_obj, coupon)
        messages.success(
            request, "Review submitted! Check your email for your discount coupon.")

        return redirect('project_detail', slug=project.slug)

    return redirect('project_list')


# ================= COUPON GENERATOR =================
def generate_coupon_for_user(user):
    # Random coupon code banao
    code = 'REVIEW' + ''.join(random.choices(string.digits, k=4))

    # Coupon create karo
    coupon = Coupon.objects.create(
        code=code,
        discount_percent=10,
        expiry_date=timezone.now().date().replace(
            year=timezone.now().year + 1
        ),
        is_active=True
    )

    # User ko assign karo
    UserCoupon.objects.create(
        user=user,
        coupon=coupon,
        is_used=False
    )

    return coupon
