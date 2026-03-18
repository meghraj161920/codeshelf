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
        identifier = request.POST.get("email").strip()
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
    user = request.user

    profile, created = Profile.objects.get_or_create(user=user)

    context = {
        "user": user,
        "profile": profile,
    }

    return render(request, "accounts/dashboard.html", {
        "user": request.user,
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