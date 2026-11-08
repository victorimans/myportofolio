from django.urls import path

from main import api_views

app_name = "api"

urlpatterns = [
    path("projects/", api_views.project_list, name="project-list"),
    path("projects/<uuid:project_id>/", api_views.project_detail, name="project-detail"),
    path("projects/<uuid:project_id>/star/", api_views.project_star, name="project-star"),
    path("blog-posts/", api_views.blogpost_list, name="blogpost-list"),
    path("blog-posts/<int:blogpost_id>/", api_views.blogpost_list, name="blogpost-detail"),
    path("blog-post/<int:blogpost_id>/star/", api_views.blogpost_list, name="blogpost-star"),
]