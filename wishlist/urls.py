from django.urls import path
from . import views

urlpatterns = [
    path('', views.wishlist, name='wishlist'),
    path('toggle/', views.toggle_wishlist, name='toggle_wishlist'),
]