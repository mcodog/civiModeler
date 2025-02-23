from django.urls import path
from .views import get_projects, create_project

urlpatterns = [
    path('projects/', get_projects, name="get_projects"),
    path('projects/create/', create_project, name="create_project"),
]
