from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('upload/', views.upload_course, name='upload_course'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
]

