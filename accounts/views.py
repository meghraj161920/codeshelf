from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.messages import get_messages
from .forms import RegisterForm
from .models import Profile
import random
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from core.decorators import seller_required, customer_required, unauthenticated_only
from wishlist.models import Wishlist
from reviews.models import Review
from coupons.models import UserCoupon
from django.db import models
from projects.models import Project
from orders.models import Order, OrderItem


User = get_user_model()


# ================= REGISTER =================
@unauthenticated_only
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            # ✅ Register se pehle cart save karo
            old_cart = request.session.get('cart', [])

            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = form.cleaned_data['role']
            profile.save()

            # ✅ Auto login karo
            login(request, user)

            # ✅ Cart restore karo
            request.session['cart'] = old_cart

            messages.success(request, "Account created successfully!")

            # ✅ Role ke hisaab se redirect
            if profile.role == 'seller':
                return redirect('seller_dashboard')
            else:
                return redirect('customer_dashboard')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


# ================= LOGIN =================
@unauthenticated_only
def login_view(request):
    if request.method == "POST":
        identifier = request.POST.get("email", "").strip()
        password = request.POST.get("password")

        # login with email OR username
        try:
            user_obj = User.objects.get(email=identifier)
            username = user_obj.username
        except User.DoesNotExist:
            username = identifier

        user = authenticate(request, username=username, password=password)

        if user:
            if user.is_superuser:
                messages.error(request, "Invalid username/email or password")
                return redirect("login")
            login(request, user)

            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            profile = getattr(user, 'profile', None)

            if profile and profile.role == "seller":
                return redirect("seller_dashboard")
            else:
                return redirect("customer_dashboard")

        else:
            messages.error(request, "Invalid username/email or password")

    return render(request, "accounts/login.html")


# ================= CUSTOMER DASHBOARD =================


@customer_required
def customer_dashboard(request):
    user = request.user

    # Recent orders
    recent_orders = Order.objects.filter(
        user=user
    ).prefetch_related('items__project').order_by('-order_date')[:5]

    # Stats
    total_orders = Order.objects.filter(user=user, is_completed=True).count()
    wishlist_count = Wishlist.objects.filter(user=user).count()
    reviews_count = Review.objects.filter(user=user).count()
    coupons_count = UserCoupon.objects.filter(user=user, is_used=False).count()

    return render(request, "accounts/customer_dashboard.html", {
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'wishlist_count': wishlist_count,
        'reviews_count': reviews_count,
        'coupons_count': coupons_count,
    })

# ================= SELLER DASHBOARD =================
@seller_required
def seller_dashboard(request):
    user = request.user

    # Seller ke projects
    projects = Project.objects.filter(seller=user).order_by('-created_at')

    # Stats
    total_projects = projects.count()
    total_orders = OrderItem.objects.filter(project__seller=user).count()
    total_revenue = OrderItem.objects.filter(
        project__seller=user
    ).aggregate(total=models.Sum('price'))['total'] or 0

    # Recent orders
    recent_orders = OrderItem.objects.filter(
        project__seller=user
    ).select_related('order__user', 'project').order_by('-order__order_date')[:10]

    return render(request, "accounts/seller_dashboard.html", {
        'projects': projects,
        'total_projects': total_projects,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
    })


# ================= USER PAGES =================
@login_required
def profile(request):
    profile = request.user.profile

    if request.method == "POST":

        phone = request.POST.get("phone")

        if phone and Profile.objects.filter(phone_number=phone).exclude(user=request.user).exists():
            messages.error(request, "Phone already used")
            return redirect("profile")

        full_name = request.POST.get("full_name")

        if full_name:
            parts = full_name.strip().split(" ", 1)
            request.user.first_name = parts[0]
            request.user.last_name = parts[1] if len(parts) > 1 else ""

        request.user.email = request.POST.get("email")

        profile.dob = request.POST.get("dob")
        profile.phone_number = phone
        profile.gender = request.POST.get("gender")

        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")

        request.user.save()
        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(request, "accounts/profile.html", {
        "profile": profile
    })


@login_required
def my_purchases(request):
    return render(request, 'accounts/my_purchases.html')


@login_required
def downloads(request):
    return render(request, 'accounts/downloads.html')


@login_required
def wishlist_view(request):
    return render(request, 'accounts/wishlist.html')


@login_required
def reviews_view(request):
    return render(request, 'accounts/reviews.html')


@login_required
def payment_view(request):
    return render(request, 'accounts/payments.html')


# ================= LOGOUT =================
@login_required
def logout_view(request):
    
    storage = get_messages(request)
    for _ in storage:
        pass

    logout(request)
    return redirect('login')




# ================= FORGOT PASSWORD =================
def forgot_view(request):

    # STEP 1 — Email submit
    if request.method == "POST" and 'send_otp' in request.POST:
        email = request.POST.get("email", "").strip()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
            return redirect('forgot')

        # OTP generate करो
        otp = random.randint(1000, 9999)

        # Session में save करो
        request.session['otp'] = otp
        request.session['otp_email'] = email

        # Terminal में print करो
        print(f"\n{'='*40}")
        print(f"  OTP for {email} : {otp}")
        print(f"{'='*40}\n")

        messages.success(request, "OTP sent! Check your terminal.")
        return render(request, 'accounts/forgot.html', {'step': 'verify', 'email': email})

    # STEP 2 — OTP verify
    if request.method == "POST" and 'verify_otp' in request.POST:
        user_otp = request.POST.get("otp", "").strip()
        email = request.session.get('otp_email')

        if str(request.session.get('otp')) == user_otp:
            return render(request, 'accounts/forgot.html', {'step': 'reset', 'email': email})
        else:
            messages.error(request, "Invalid OTP. Try again.")
            return render(request, 'accounts/forgot.html', {'step': 'verify', 'email': email})

    # STEP 3 — New password set
    if request.method == "POST" and 'reset_password' in request.POST:
        email = request.session.get('otp_email')
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/forgot.html', {'step': 'reset', 'email': email})

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, 'accounts/forgot.html', {'step': 'reset', 'email': email})

        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()

            # Session पूरी तरह clear करो
            request.session.flush()

            messages.success(request, "Password reset successful! Please login.")
            return redirect('login')

        except User.DoesNotExist:
            messages.error(request, "Something went wrong.")
            return redirect('forgot')

    # GET request — fresh page
    return render(request, 'accounts/forgot.html', {'step': 'email'})