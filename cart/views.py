from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from projects.models import Project
from orders.models import OrderItem
from django.contrib import messages



@login_required
def add_to_cart(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    cart = request.session.get('cart', [])

    # ✅ Check 1 — Already purchased?
    already_purchased = OrderItem.objects.filter(
        order__user=request.user,
        order__is_completed=True,
        project=project
    ).exists()

    if already_purchased:
        messages.error(request, f"You have already purchased '{project.title}'.")
        return redirect('project_detail', slug=project.slug)

    # ✅ Check 2 — Already in cart?
    if project_id not in cart:
        cart.append(project_id)
        request.session['cart'] = cart
        status = 'added'
    else:
        status = 'already_in_cart'

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': status, 'cart_count': len(cart)})

    return redirect('cart')


@login_required
def cart_view(request):
    cart = request.session.get('cart', [])
    projects = Project.objects.filter(id__in=cart)
    total = sum(p.price for p in projects)

    return render(request, 'cart/cart.html', {
        'projects': projects,
        'total': total,
        'cart_count': len(cart)
    })


@login_required
def remove_from_cart(request, project_id):
    cart = request.session.get('cart', [])
    if project_id in cart:
        cart.remove(project_id)
        request.session['cart'] = cart

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        projects = Project.objects.filter(id__in=cart)
        total = sum(p.price for p in projects)
        return JsonResponse({'status': 'removed', 'cart_count': len(cart), 'total': str(total)})

    return redirect('cart')


@login_required
def clear_cart(request):
    request.session['cart'] = []
    return redirect('cart')


def cart_count(request):
    cart = request.session.get('cart', [])
    return JsonResponse({'cart_count': len(cart)})


def cart_context(request):
    cart = request.session.get('cart', [])
    return {'cart_count': len(cart)}