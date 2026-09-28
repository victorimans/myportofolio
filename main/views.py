from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import redirect_to_login
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Exists, OuterRef
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from main.forms import BlogPostForm, ProjectForm
from main.models import BlogPost, Experience, Project


def can_edit(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name="Editor").exists()
    )


def protected(allowed, methods):
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path(), reverse("main:login"))
            if not allowed(request.user):
                raise PermissionDenied
            if request.method not in methods:
                return HttpResponseNotAllowed(methods)
            return view(request, *args, **kwargs)

        return wrapped

    return decorator


def is_owner(user):
    return user.is_superuser


def is_member(user):
    return user.is_authenticated


@require_GET
def show_project_detail(request, id):
    project = get_object_or_404(projects_for_user(request.user), pk=id)
    return render(request, "project.html", {
        "name": "Victoriano Iman Santosa", "project_list": [project],
        "title_query": "", "is_detail": True, "can_edit": can_edit(request.user),
    })


def projects_for_user(user):
    projects = Project.objects.annotate(star_count=Count("starred_by", distinct=True))
    if user.is_authenticated:
        membership = Project.starred_by.through.objects.filter(project_id=OuterRef("pk"), user_id=user.pk)
        projects = projects.annotate(is_starred=Exists(membership))
    return projects


@require_http_methods(["GET", "POST"])
def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Victoriano Iman Santosa",
        "form": form,
    }
    return render(request, "register.html", context)


@require_http_methods(["GET", "POST"])
def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    next_url = request.POST.get("next", "") if request.method == "POST" else request.GET.get("next", "")
    if not url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=request.is_secure()):
        next_url = ""

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(next_url or "main:show_main")

    context = {
        "name": "Victoriano Iman Santosa",
        "form": form,
        "next_url": next_url,
    }
    return render(request, "login.html", context)


@require_POST
def logout_user(request):
    logout(request)
    return redirect("main:show_main")


@require_GET
def show_main(request):
    context = {
        "name": "Victoriano Iman Santosa",
        "npm": "2506544353",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "CS student at University Of Indonesia | Silver Medalist – Indonesia National Olympiad in Informatics (NOI) 2024 | Informatics Olympiad Coach"
        ),
    }
    return render(request, "index.html", context)


@require_GET
def show_experience(request):
    context = {
        "name": "Victoriano Iman Santosa",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


@require_GET
def show_projects(request):
    json_response = get_projects_json(request)
    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    project_ids = [project.object.pk for project in projects]
    title_query = request.GET.get("title", "").strip()
    projects = list(projects_for_user(request.user).filter(pk__in=project_ids))
    context = {
        "name": "Victoriano Iman Santosa",
        "project_list": projects,
        "title_query": title_query,
        "can_edit": can_edit(request.user),
    }
    return render(request, "project.html", context)


@protected(is_owner, ["GET", "POST"])
def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Victoriano Iman Santosa",
        "form": form,
    }
    return render(request, "projects_form.html", context)


@protected(is_owner, ["POST"])
def delete_project(request, id):
    project = get_object_or_404(Project, pk=id)
    project.delete()
    messages.success(request, "Proyek berhasil dihapus!")
    return redirect("main:show_projects")


@protected(is_member, ["POST"])
def toggle_star(request, project_id):
    with transaction.atomic():
        project = get_object_or_404(Project.objects.select_for_update(), pk=project_id)
        if project.starred_by.filter(pk=request.user.pk).exists():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)
    return redirect("main:show_projects")


@protected(can_edit, ["GET", "POST"])
def update_project(request, id):
    project = get_object_or_404(Project, pk=id)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek berhasil diperbarui!")
        return redirect("main:show_projects")
    return render(request, "projects_form.html", {
        "name": "Victoriano Iman Santosa", "form": form,
        "project": project, "is_update": True,
    })


@require_GET
def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects, fields=["title", "description", "tech_stack", "project_url", "project_image_url"])
    return HttpResponse(projects_json, content_type="application/json")


@require_GET
def show_json_by_id(request, id):
    project = get_object_or_404(Project, pk=id)
    data = serializers.serialize("json", [project], fields=["title", "description", "tech_stack", "project_url", "project_image_url"])
    return HttpResponse(data, content_type="application/json")


@protected(is_owner, ["GET", "POST"])
def create_blog(request):
    form = BlogPostForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Blog baru berhasil ditambahkan!")
        return redirect("main:show_blog")

    context = {
        "name": "Victoriano Iman Santosa",
        "form": form,
        "form_title": "Add New Blog",
        "submit_label": "Tambah Blog",
        "is_update": False,
    }
    return render(request, "blog_form.html", context)


@protected(can_edit, ["GET", "POST"])
def update_blog(request, id):
    blog_post = get_object_or_404(BlogPost, pk=id)
    form = BlogPostForm(request.POST or None, instance=blog_post)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Blog berhasil diperbarui!")
        return redirect("main:show_blog")

    context = {
        "name": "Victoriano Iman Santosa",
        "form": form,
        "blog_post": blog_post,
        "form_title": "Edit Blog",
        "submit_label": "Simpan Perubahan",
        "is_update": True,
    }
    return render(request, "blog_form.html", context)


@protected(is_owner, ["POST"])
def delete_blog(request, id):
    blog_post = get_object_or_404(BlogPost, pk=id)
    blog_post.delete()
    messages.success(request, "Blog berhasil dihapus!")
    return redirect("main:show_blog")


@require_GET
def get_blog_json(request):
    blog_posts = BlogPost.objects.order_by("-created_at", "-id")
    blog_posts_json = serializers.serialize("json", blog_posts, use_natural_foreign_keys=True)
    return HttpResponse(blog_posts_json, content_type="application/json")


@require_GET
def show_blog_json_by_id(request, id):
    blog_post = get_object_or_404(BlogPost, pk=id)
    data = serializers.serialize("json", [blog_post])
    return HttpResponse(data, content_type="application/json")


@require_GET
def show_blog(request):
    json_response = get_blog_json(request)
    blog_posts = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    blog_posts = [blog_post.object for blog_post in blog_posts]

    context = {
        "name": "Victoriano Iman Santosa",
        "blog_posts": blog_posts,
        "can_edit": can_edit(request.user),
    }
    return render(request, "blog.html", context)

