from orders.models import Order
from django.utils import timezone

def is_coupon_valid(coupon_code, user, cart_items_count=0):
    """
    Checks if a given global coupon code is valid for the user and their cart.
    Returns (is_valid, error_message).
    """
    code = coupon_code.upper()
    
    if code == 'SAVE5':
        return True, ""
        
    elif code == 'WELCOME10':
        has_orders = Order.objects.filter(user=user, is_completed=True).exists()
        if has_orders:
            return False, "This coupon is only for your first purchase."
        return True, ""
        
    elif code == 'COMBO15':
        if cart_items_count < 2:
            return False, "This coupon requires at least 2 items in your cart."
        return True, ""
        
    elif code == 'BIRTHDAY20':
        dob = user.profile.dob
        if not dob:
            return False, "You haven't set your birthday in your profile."
        today = timezone.now().date()
        if dob.month == today.month and dob.day == today.day:
            return True, ""
        return False, "This coupon is only valid on your birthday!"
        
    # By default, if it's a global coupon without specific rules, just return True
    return True, ""
