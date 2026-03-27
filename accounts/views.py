from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.messages import get_messages

from .forms import RegisterForm
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from core.decorators import seller_required, customer_required, unauthenticated_only

User = get_user_model()


# ================= REGISTER =================
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # create profile safely
            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = form.cleaned_data['role']
            profile.save()

            messages.success(request, "Account created successfully!")
            return redirect('login')
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
            login(request, user)

            # ✅ TASK 1: NEXT REDIRECT FIX
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            profile = getattr(user, 'profile', None)

            if user.is_superuser:
                return redirect("/admin/")
            elif profile and profile.role == "seller":
                return redirect("seller_dashboard")
            else:
                return redirect("home")

        else:
            messages.error(request, "Invalid username/email or password")

    return render(request, "accounts/login.html")


# ================= CUSTOMER DASHBOARD =================
@customer_required
def dashboard(request):
    profile = request.user.profile

    if request.method == "POST":

        phone = request.POST.get("phone")

        if phone and Profile.objects.filter(phone_number=phone).exclude(user=request.user).exists():
            messages.error(request, "Phone already used")
            return redirect("dashboard")

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
        return redirect("dashboard")

    return render(request, "accounts/dashboard.html", {
        "profile": profile
    })


# ================= SELLER DASHBOARD =================
@seller_required
def seller_dashboard(request):
    return render(request, "accounts/seller_dashboard.html")


# ================= USER PAGES =================
@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


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
    
    # ✅ Clear all messages
    storage = get_messages(request)
    for _ in storage:
        pass

    logout(request)
    return redirect('login')


# ================= FORGOT PASSWORD =================
def forgot_view(request):
    return render(request, 'accounts/forgot.html')