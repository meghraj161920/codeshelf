from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
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
from coupons.models import UserCoupon, Coupon
from coupons.utils import is_coupon_valid
from django.db import models
from projects.models import Project
from orders.models import Order, OrderItem
from courses.models import Course


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
            
            selected_role = form.cleaned_data['role']
            if selected_role == 'both':
                profile.is_customer_account = True
                profile.is_seller_account = True
                profile.role = 'customer' # default active role
            elif selected_role == 'seller':
                profile.is_seller_account = True
                profile.role = 'seller'
            else:
                profile.is_customer_account = True
                profile.role = 'customer'
                
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
            # BUG FIX: Safely handle multiple users with the same email
            user_obj = User.objects.filter(email=identifier).first()
            if user_obj:
                username = user_obj.username
            else:
                username = identifier
        except Exception:
            username = identifier

        user = authenticate(request, username=username, password=password)

        if user:
            if user.is_superuser or user.is_staff:
                messages.error(request, "Invalid username/email or password")
                return redirect("login")
            login(request, user)

            if request.POST.get('remember'):
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)  # Browser close

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
    ).prefetch_related('items__project').order_by('-order_date')[:4]

    # Stats
    total_orders = Order.objects.filter(user=user, is_completed=True).count()
    wishlist_count = Wishlist.objects.filter(user=user).count()
    reviews_count = Review.objects.filter(user=user).count()
    user_coupons_count = UserCoupon.objects.filter(user=user, is_used=False).count()

    all_global_coupons = Coupon.objects.filter(is_active=True, is_global=True)
    used_coupons = UserCoupon.objects.filter(user=user, is_used=True).values_list('coupon_id', flat=True)
    all_global_coupons = all_global_coupons.exclude(id__in=used_coupons)
    
    global_coupons_count = 0
    for c in all_global_coupons:
        valid, _ = is_coupon_valid(c.code, user, cart_items_count=2)
        if valid:
            global_coupons_count += 1

    coupons_count = user_coupons_count + global_coupons_count

    return render(request, "accounts/customer_dashboard.html", {
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'wishlist_count': wishlist_count,
        'reviews_count': reviews_count,
        'coupons_count': coupons_count,
    })

from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
import json

# ================= SELLER DASHBOARD =================
@seller_required
def seller_dashboard(request):
    user = request.user

    # Seller ke projects and courses
    projects = Project.objects.filter(seller=user).order_by('-created_at')
    # If there's a need to display courses here later, we can add:
    courses = Course.objects.filter(seller=user).order_by('-created_at')

    # Stats
    total_projects = projects.count()
    total_courses = courses.count()

    seller_items = OrderItem.objects.filter(
        Q(project__seller=user) | Q(course__seller=user),
        order__is_completed=True
    )

    total_orders = seller_items.count()
    total_revenue = seller_items.aggregate(total=Sum('price'))['total'] or 0

    # Recent orders
    recent_orders = seller_items.select_related(
        'order__user', 'project', 'course'
    ).order_by('-order__order_date')[:10]

    # Analytics for Chart.js (Monthly Revenue)
    monthly_sales = seller_items.annotate(
        month=TruncMonth('order__order_date')
    ).values('month').annotate(
        revenue=Sum('price'),
        orders=models.Count('id')
    ).order_by('month')

    months = []
    revenues = []
    order_counts = []
    
    for entry in monthly_sales:
        if entry['month']:
            months.append(entry['month'].strftime('%b %Y'))
            revenues.append(float(entry['revenue']))
            order_counts.append(entry['orders'])

    return render(request, "accounts/seller_dashboard.html", {
        'projects': projects,
        'courses': courses,
        'total_projects': total_projects,
        'total_courses': total_courses,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'chart_months': json.dumps(months),
        'chart_revenues': json.dumps(revenues),
        'chart_orders': json.dumps(order_counts),
    })


# ================= EARNINGS PAGE =================
@seller_required
def earnings_view(request):
    user = request.user

    seller_items = OrderItem.objects.filter(
        Q(project__seller=user) | Q(course__seller=user),
        order__is_completed=True
    )

    total_orders = seller_items.count()
    total_revenue = seller_items.aggregate(total=Sum('price'))['total'] or 0

    # Analytics for Chart.js (Monthly Revenue)
    monthly_sales = seller_items.annotate(
        month=TruncMonth('order__order_date')
    ).values('month').annotate(
        revenue=Sum('price'),
        orders=models.Count('id')
    ).order_by('month')

    months = []
    revenues = []
    order_counts = []
    
    for entry in monthly_sales:
        if entry['month']:
            months.append(entry['month'].strftime('%b %Y'))
            revenues.append(float(entry['revenue']))
            order_counts.append(entry['orders'])

    return render(request, "accounts/earnings.html", {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'chart_months': json.dumps(months),
        'chart_revenues': json.dumps(revenues),
        'chart_orders': json.dumps(order_counts),
    })


# ================= USER PAGES =================
@login_required
def profile(request):
    profile = request.user.profile

    if request.method == "POST":

        country_code = request.POST.get("country_code", "+91")
        phone_number = request.POST.get("phone", "").strip()
        
        if phone_number.startswith(country_code):
            phone_number = phone_number[len(country_code):].strip()
            
        phone = f"{country_code}{phone_number}" if phone_number else ""

        if phone and Profile.objects.filter(phone_number=phone).exclude(user=request.user).exists():
            messages.error(request, "Phone already used")
            return redirect("profile")

        full_name = request.POST.get("full_name")

        if full_name:
            parts = full_name.strip().split(" ", 1)
            request.user.first_name = parts[0]
            request.user.last_name = parts[1] if len(parts) > 1 else ""

        new_email = request.POST.get("email")
        if new_email is not None:
            request.user.email = new_email

        dob_val = request.POST.get("dob")
        profile.dob = dob_val if dob_val else None
        profile.phone_number = phone
        profile.gender = request.POST.get("gender")
        profile.about = request.POST.get("about")

        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")

        request.user.save()
        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    phone_code = "+91"
    phone_number_only = profile.phone_number or ""
    
    for code in ["+91", "+1", "+44", "+971", "+61"]:
        if phone_number_only.startswith(code):
            phone_code = code
            phone_number_only = phone_number_only[len(code):]
            break

    return render(request, "accounts/profile.html", {
        "profile": profile,
        "phone_code": phone_code,
        "phone_number_only": phone_number_only
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


# ================= PUBLIC SELLER STOREFRONT =================
def seller_profile(request, username):
    seller_user = get_object_or_404(User, username=username, profile__role='seller')
    
    projects = Project.objects.filter(seller=seller_user, is_active=True).order_by('-created_at')
    courses = Course.objects.filter(seller=seller_user, is_active=True).order_by('-created_at')
    
    return render(request, "accounts/seller_profile.html", {
        'seller_user': seller_user,
        'projects': projects,
        'courses': courses,
    })


@login_required
def reviews_view(request):
    return render(request, 'accounts/reviews.html')


@login_required
def payment_view(request):
    from orders.models import Order
    from django.db.models import Sum

    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    
    total_spent = orders.filter(is_completed=True).aggregate(total=Sum('total_amount'))['total'] or 0

    return render(request, 'accounts/payments.html', {
        'orders': orders,
        'total_spent': total_spent,
    })


# ================= LOGOUT =================
@login_required
def logout_view(request):
    
    storage = get_messages(request)
    for _ in storage:
        pass

    logout(request)
    return redirect('login')


# ================= SWITCH ROLE =================
@login_required
def switch_role(request):
    if request.method == "POST":
        profile = request.user.profile
        if not (profile.is_seller_account and profile.is_customer_account):
            messages.error(request, "You need both Customer and Seller roles to switch.")
            return redirect('profile')

        if profile.role == 'customer':
            profile.role = 'seller'
            messages.success(request, "Switched to Seller Dashboard")
            next_url = 'seller_dashboard'
        else:
            profile.role = 'customer'
            messages.success(request, "Switched to Customer Dashboard")
            next_url = 'customer_dashboard'
        profile.save()
        return redirect(next_url)
    return redirect('profile')


# ================= UPGRADE ROLE =================
@login_required
def upgrade_role(request):
    if request.method == "POST":
        profile = request.user.profile
        action = request.POST.get('action')
        
        if action == 'become_seller':
            profile.is_seller_account = True
            profile.role = 'seller'
            profile.save()
            messages.success(request, "Congratulations! You are now a Seller.")
            return redirect('seller_dashboard')
            
        elif action == 'become_customer':
            profile.is_customer_account = True
            profile.role = 'customer'
            profile.save()
            messages.success(request, "You now have a Customer account as well.")
            return redirect('customer_dashboard')
            
    return redirect('profile')


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

        # Send HTML email with OTP
        subject = 'Password Reset OTP - CodeShelf'
        html_message = render_to_string('emails/otp_email.html', {'otp': otp})
        plain_message = strip_tags(html_message)
        
        try:
            msg = EmailMultiAlternatives(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )
            msg.attach_alternative(html_message, "text/html")
            msg.send(fail_silently=False)
            
            messages.success(request, "OTP sent! Please check your email.")
        except Exception as e:
            print(f"Failed to send email: {e}")
            messages.error(request, "Failed to send email. Please try again later.")
            
        return render(request, 'accounts/forgot.html', {'step': 'verify', 'email': email})

    # STEP 2 — OTP verify
    if request.method == "POST" and 'verify_otp' in request.POST:
        user_otp = request.POST.get("otp", "").strip()
        email = request.session.get('otp_email')

        # In step 2 - OTP verify
        if str(request.session.get('otp')) == user_otp:
            request.session['otp_verified'] = True
            return render(request, 'accounts/forgot.html', {'step': 'reset', 'email': email})
        else:
            # BUG FIX: Clear the OTP so they have to request a new one (prevents brute-force)
            request.session.pop('otp', None)
            messages.error(request, "Invalid OTP. Please request a new one.")
            return render(request, 'accounts/forgot.html', {'step': 'email'})

    # STEP 3 — New password set
    if request.method == "POST" and 'reset_password' in request.POST:
        if not request.session.get('otp_verified'):
            messages.error(request, "Unauthorized request. Please verify OTP first.")
            return redirect('forgot')

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
            user = User.objects.filter(email=email).first()
            if user:
                user.set_password(password)
                user.save()

            # Session पूरी तरह clear करो
            request.session.flush()

            messages.success(request, "Password reset successful! Please login.")
            return redirect('login')

        except Exception:
            messages.error(request, "Something went wrong.")
            return redirect('forgot')

    # GET request — fresh page
    return render(request, 'accounts/forgot.html', {'step': 'email'})