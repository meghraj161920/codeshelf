from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:project_id>/', views.add_to_cart, name='add_to_cart'),
]