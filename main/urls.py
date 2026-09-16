from django.urls import path

from main.views import (
    create_blog,
    create_project,
    delete_project,
    show_blog,
    show_experience,
    get_projects_json,
    show_json_by_id,
    show_main,
    show_projects,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("projects/", show_projects, name="show_projects"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/<uuid:id>/delete/", delete_project, name="delete_project"),
    path("experience/", show_experience, name="show_experience"),
    path("blog/add/", create_blog, name="create_blog"),
    path("blog/", show_blog, name="show_blog"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("json/<uuid:id>/", show_json_by_id, name="show_json_by_id"),
]
