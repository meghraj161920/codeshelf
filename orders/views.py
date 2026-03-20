from django.shortcuts import redirect, render


def orders(request):
    return render(request, 'accounts/my_purchases.html')


def checkout(request):

    order_items = [
        {"title": "E-commerce Website Project", "price": 499},
        {"title": "Chat Application Project", "price": 299},
    ]

    subtotal = sum(item["price"] for item in order_items)
    discount = request.session.get("discount", 0)
    total = subtotal - discount

    context = {
        "order_items": order_items,
        "subtotal": subtotal,
        "discount": discount,
        "total": total,
    }

    return render(request, "orders/checkout.html", context)


def place_order(request):
    request.session.pop("discount", None)
    return redirect('order_success', order_id="ORD12345")


def order_success(request, order_id):

    context = {
        "order_id": order_id
    }

    return render(request, "orders/order_success.html", context)


def order_history(request):

    orders = [
        {
            "id": "ORD12345",
            "date": "12 Feb 2026",
            "items": [
                {"title": "E-commerce Website Project", "price": 499},
                {"title": "Chat Application Project", "price": 299},
            ],
            "total": 798,
        },
        {
            "id": "ORD12344",
            "date": "05 Feb 2026",
            "items": [
                {"title": "Portfolio Website Project", "price": 199},
            ],
            "total": 199,
        },
    ]

    return render(request, "orders/order_history.html", {"orders": orders})
