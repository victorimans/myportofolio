from django.urls import path

from main.views import (
    create_blog,
    create_blog_ajax,
    create_project,
    create_project_ajax,
    delete_blog,
    delete_project,
    get_blog_json,
    get_projects_json,
    login_user,
    logout_user,
    register,
    show_blog,
    show_blog_json_by_id,
    show_experience,
    show_json_by_id,
    show_main,
    show_projects,
    show_project_detail,
    toggle_star,
    toggle_blog_star,
    update_project,
    update_blog,
)


app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("projects/", show_projects, name="show_projects"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/add-ajax/", create_project_ajax, name="create_project_ajax"),
    path("projects/<uuid:id>/", show_project_detail, name="show_project_detail"),
    path("projects/<uuid:id>/edit/", update_project, name="update_project"),
    path("projects/<uuid:id>/delete/", delete_project, name="delete_project"),
    path("projects/<uuid:project_id>/star/", toggle_star, name="toggle_star"),
    path("experience/", show_experience, name="show_experience"),
    path("blog/add/", create_blog, name="create_blog"),
    path("blog/add-ajax/", create_blog_ajax, name="create_blog_ajax"),
    path("blog/<int:id>/edit/", update_blog, name="update_blog"),
    path("blog/<int:id>/delete/", delete_blog, name="delete_blog"),
    path("blog/<int:blog_id>/star/", toggle_blog_star, name="toggle_blog_star"),
    path("blog/", show_blog, name="show_blog"),
    path("api/blog/", get_blog_json, name="get_blog_json"),
    path("api/blog/<int:id>/", show_blog_json_by_id, name="show_blog_json_by_id"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("json/<uuid:id>/", show_json_by_id, name="show_json_by_id"),

]
