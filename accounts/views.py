from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import RegisterForm
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            messages.success(request, "Account created successfully!")
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        identifier = request.POST.get("email", "").strip()
        password = request.POST.get("password")

        user_obj = User.objects.filter(email=identifier).first()

        if user_obj:
            username = user_obj.username
        else:
            username = identifier

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username/email or password")

    return render(request, "accounts/login.html")


@login_required
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


def profile(request):
    return render(request, 'accounts/profile.html')


def my_purchases(request):
    return render(request, 'accounts/my_purchases.html')


def downloads(request):
    return render(request, 'accounts/downloads.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def forgot_view(request):
    return render(request, 'accounts/forgot.html')


def wishlist_view(request):
    return render(request, 'accounts/wishlist.html')


def reviews_view(request):
    return render(request, 'accounts/reviews.html')


def payment_view(request):
    return render(request, 'accounts/payments.html')
