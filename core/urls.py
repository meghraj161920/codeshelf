from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('faq/', views.faq, name='faq'),
    path('refund_policy/', views.refund_policy, name='refund_policy'),
    path('search/', views.global_search, name='global_search'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('submit-testimonial/', views.submit_testimonial, name='submit_testimonial'),
]