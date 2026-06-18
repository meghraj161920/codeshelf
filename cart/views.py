from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from projects.models import Project
from courses.models import Course
from orders.models import OrderItem
from wishlist.models import Wishlist
from django.contrib import messages

def get_cart_dict(request):
    cart = request.session.get('cart', {'projects': [], 'courses': []})
    if isinstance(cart, list):
        cart = {'projects': [str(x) for x in cart], 'courses': []}
        request.session['cart'] = cart
    return cart

@login_required
def add_to_cart(request, item_type, item_id):
    cart = get_cart_dict(request)
    
    if item_type == 'project':
        item = get_object_or_404(Project, id=item_id)
        already_purchased = OrderItem.objects.filter(order__user=request.user, order__is_completed=True, project=item).exists()
    elif item_type == 'course':
        item = get_object_or_404(Course, id=item_id)
        already_purchased = OrderItem.objects.filter(order__user=request.user, order__is_completed=True, course=item).exists()
    else:
        return JsonResponse({'error': 'Invalid item type'}, status=400)

    if already_purchased:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'already_purchased', 'cart_count': len(cart['projects']) + len(cart['courses'])})
        messages.error(request, f"You have already purchased '{item.title}'.")
        return redirect('cart')

    item_id_str = str(item_id)
    if item_id_str not in cart[f"{item_type}s"]:
        cart[f"{item_type}s"].append(item_id_str)
        request.session['cart'] = cart
        status = 'added'
    else:
        status = 'already_in_cart'

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': status, 'cart_count': len(cart['projects']) + len(cart['courses'])})

    return redirect('cart')

@login_required
def cart_view(request):
    cart = get_cart_dict(request)
    projects = Project.objects.filter(id__in=cart['projects'])
    courses = Course.objects.filter(id__in=cart['courses'])
    
    total = sum(p.price for p in projects) + sum(c.price for c in courses)
    
    return render(request, 'cart/cart.html', {
        'projects': projects,
        'courses': courses,
        'total': total,
        'cart_count': len(cart['projects']) + len(cart['courses'])
    })

@login_required
def remove_from_cart(request, item_type, item_id):
    cart = get_cart_dict(request)
    if item_type in ['project', 'course']:
        list_key = f"{item_type}s"
        cart[list_key] = [str(pid) for pid in cart[list_key] if str(pid) != str(item_id)]
        request.session['cart'] = cart

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        projects = Project.objects.filter(id__in=cart['projects'])
        courses = Course.objects.filter(id__in=cart['courses'])
        total = sum(p.price for p in projects) + sum(c.price for c in courses)
        return JsonResponse({
            'status': 'removed', 
            'cart_count': len(cart['projects']) + len(cart['courses']), 
            'total': str(total)
        })

    return redirect('cart')

@login_required
def clear_cart(request):
    request.session['cart'] = {'projects': [], 'courses': []}
    return redirect('cart')

def cart_count(request):
    cart = get_cart_dict(request)
    return JsonResponse({'cart_count': len(cart['projects']) + len(cart['courses'])})

def cart_context(request):
    cart = get_cart_dict(request)
    cart_project_ids = [int(i) for i in cart['projects']]
    cart_course_ids = [int(i) for i in cart['courses']]
    
    wishlist_project_ids = []
    wishlist_course_ids = []
    purchased_project_ids = []
    purchased_course_ids = []
    if request.user.is_authenticated:
        wishlist_project_ids = list(Wishlist.objects.filter(user=request.user, project__isnull=False).values_list('project_id', flat=True))
        wishlist_course_ids = list(Wishlist.objects.filter(user=request.user, course__isnull=False).values_list('course_id', flat=True))
        
        purchased_project_ids = list(OrderItem.objects.filter(
            order__user=request.user, order__is_completed=True, project__isnull=False
        ).values_list('project_id', flat=True))
        
        purchased_course_ids = list(OrderItem.objects.filter(
            order__user=request.user, order__is_completed=True, course__isnull=False
        ).values_list('course_id', flat=True))

    return {
        'cart_count': len(cart['projects']) + len(cart['courses']),
        'global_cart_project_ids': cart_project_ids,
        'global_cart_course_ids': cart_course_ids,
        'global_wishlist_project_ids': wishlist_project_ids,
        'global_wishlist_course_ids': wishlist_course_ids,
        'wishlist_count': len(wishlist_project_ids) + len(wishlist_course_ids),
        'global_purchased_project_ids': purchased_project_ids,
        'global_purchased_course_ids': purchased_course_ids,
    }