from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/<str:item_type>/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<str:item_type>/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('count/', views.cart_count, name='cart_count'),
]