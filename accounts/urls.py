from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot/', views.forgot_view, name='forgot'),
    path('profile/', views.profile, name='profile'),
    path('purchases/', views.my_purchases, name='my_purchases'),
    path('downloads/', views.downloads, name='downloads'),
    path('logout/', views.logout_view, name='logout'),
    path('reviews/', views.reviews_view, name='reviews'),
    path('seller/<str:username>/', views.seller_profile, name='seller_profile'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('payments/', views.payment_view, name='payments'),
    path('earnings/', views.earnings_view, name='earnings'),
    path('seller_dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('switch-role/', views.switch_role, name='switch_role'),
    path('upgrade-role/', views.upgrade_role, name='upgrade_role'),
]