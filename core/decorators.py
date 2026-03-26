from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from functools import wraps

def seller_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.profile.role != 'seller':
            # This returns a standard 403 Forbidden page
            return HttpResponseForbidden("Access denied. Seller account required.")
        return view_func(request, *args, **kwargs)
    return wrapper

def customer_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.profile.role != 'customer':
            return HttpResponseForbidden("Access denied. Customer account required.")
        return view_func(request, *args, **kwargs)
    return wrapper
