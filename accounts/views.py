from django.shortcuts import render

def login_view(request):
    return render(request, 'accounts/login.html')

def register_view(request):
    return render(request, 'accounts/register.html')

def dashboard(request):
    user_data = {
        'first_name': 'Kshitij',
        'last_name': 'Patil',
        'dob': '20/01/2022',
        'gender': 'male',
        'country_iso': 'IND',
        'phone_code': '+91',
        'phone_number': '123456789',
        'email': 'abcd1234@email.com'
    }

    return render(request, 'accounts/dashboard.html', {'user_data': user_data})

def profile(request):
    return render(request, 'accounts/profile.html')

def my_purchases(request):
    return render(request, 'accounts/my_purchases.html')

def downloads(request):
    return render(request, 'accounts/downloads.html')

def logout_view(request):
    return render(request, 'core/home.html')  # temp
