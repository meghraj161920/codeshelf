from django.urls import path
from . import views

urlpatterns = [
    path('', views.orders, name='orders'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('success/<str:order_id>/', views.order_success, name='order_success'),
    path('history/', views.order_history, name='order_history'),
]
