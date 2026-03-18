from django.urls import path
from . import views

urlpatterns = [
    path('', views.coupons, name='coupons'),
    path("apply/", views.apply_coupon, name="apply_coupon"),
]
