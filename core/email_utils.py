from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_order_confirmation_email(user, order):
    """
    Sends order confirmation email to the user after successful purchase.
    Uses HTML template for a professional look.
    """
    subject = f"Order Confirmed! #{order.id} - CodeShelf"

    html_content = render_to_string('emails/order_confirmation.html', {
        'user': user,
        'order': order,
    })

    email = EmailMultiAlternatives(
        subject=subject,
        body=f"Your order #{order.id} has been confirmed. Total: ₹{order.total_amount}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.attach_alternative(html_content, "text/html")

    try:
        email.send()
        print(f"Order confirmation email sent to {user.email}")
    except Exception as e:
        print(f"Email sending failed: {e}")
