from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('forgot/', views.forgot_view, name='forgot'),
    path('profile/', views.profile, name='profile'),
    path('purchases/', views.my_purchases, name='my_purchases'),
    path('downloads/', views.downloads, name='downloads'),
    path('logout/', views.logout_view, name='logout'),
]