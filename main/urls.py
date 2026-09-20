from django.urls import path

from main.views import (
    create_blog,
    create_project,
    delete_blog,
    delete_project,
    get_blog_json,
    get_projects_json,
    show_blog,
    show_blog_json_by_id,
    show_experience,
    show_json_by_id,
    show_main,
    show_projects,
    update_blog,
)


app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("projects/", show_projects, name="show_projects"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/<uuid:id>/delete/", delete_project, name="delete_project"),
    path("experience/", show_experience, name="show_experience"),
    path("blog/add/", create_blog, name="create_blog"),
    path("blog/<int:id>/edit/", update_blog, name="update_blog"),
    path("blog/<int:id>/delete/", delete_blog, name="delete_blog"),
    path("blog/", show_blog, name="show_blog"),
    path("api/blog/", get_blog_json, name="get_blog_json"),
    path("api/blog/<int:id>/", show_blog_json_by_id, name="show_blog_json_by_id"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("json/<uuid:id>/", show_json_by_id, name="show_json_by_id"),

]
