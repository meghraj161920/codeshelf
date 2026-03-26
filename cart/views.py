from django.shortcuts import redirect
from projects.models import Project

def add_to_cart(request, project_id):
    cart = request.session.get('cart', {})

    if str(project_id) in cart:
        cart[str(project_id)] += 1
    else:
        cart[str(project_id)] = 1

    request.session['cart'] = cart

    return redirect('project_list')  # change if needed