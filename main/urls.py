from django.urls import path

from main.views import (
    create_project,
    show_blog,
    show_experience,
    show_json,
    show_json_by_id,
    show_main,
    show_projects,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("projects/", show_projects, name="show_projects"),
    path("projects/add/", create_project, name="create_project"),
    path("experience/", show_experience, name="show_experience"),
    path("blog/", show_blog, name="show_blog"),
    path("json/", show_json, name="show_json"),
    path("json/<uuid:id>/", show_json_by_id, name="show_json_by_id"),
]
