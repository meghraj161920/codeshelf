from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    # path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('forgot/', views.forgot_view, name='forgot'),
]