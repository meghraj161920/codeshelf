from django.urls import path
from . import views

urlpatterns = [
    path('', views.review_list, name='reviews'), 
    path('add/', views.add_review, name='add_review'),
]