from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('upload/', views.upload_project, name='upload_project'),
    path('delete/<int:project_id>/', views.delete_project, name='delete_project'),
    path('download/<int:project_id>/', views.download_project, name='download_project'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),  # ✅ moved above slug
    path('<slug:slug>/', views.project_detail, name='project_detail'),  # ✅ slug always last
]