from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def role_required(allowed_roles):
    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # ✅ Not logged in → go to login (NO message)
            if not request.user.is_authenticated:
                return redirect('login')

            profile = getattr(request.user, 'profile', None)

            # ❌ Role not allowed
            if not profile or profile.role not in allowed_roles:

                # ✅ Prevent duplicate messages
                existing_messages = [m.message for m in messages.get_messages(request)]
                if "You are not authorized to access this page." not in existing_messages:
                    messages.error(request, "You are not authorized to access this page.")

                return redirect('home')

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def seller_required(view_func):
    return role_required(['seller'])(view_func)


def customer_required(view_func):
    return role_required(['customer'])(view_func)


def unauthenticated_only(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if request.user.is_authenticated:
            # Redirect based on role
            profile = getattr(request.user, 'profile', None)

            if request.user.is_superuser:
                return redirect('/admin/')
            elif profile and profile.role == 'seller':
                return redirect('seller_dashboard')
            else:
                return redirect('dashboard')

        return view_func(request, *args, **kwargs)

    return wrapper