from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('<int:id>/', views.project_detail, name='project_detail'),
]