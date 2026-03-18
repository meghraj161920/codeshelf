from django.shortcuts import render

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

    context = {
        'user_data': user_data
    }
    
    return render(request, 'accounts/dashboard.html', context)

def register_view(request):
    return render(request, 'accounts/register.html')

def login_view(request):
    return render(request, 'accounts/login.html')

def forgot_view(request):
    return render(request, 'accounts/forgot.html')