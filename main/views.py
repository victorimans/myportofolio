import secrets

from django.conf import settings
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from main.forms import BlogPostForm, ProjectForm
from main.models import BlogPost, Experience, Project


def _has_valid_write_secret(request):
    configured_secret = settings.PORTFOLIO_WRITE_SECRET
    provided_secret = request.headers.get("X-Portfolio-Write-Secret")

    if provided_secret is None:
        provided_secret = request.POST.get("secret", "")

    return bool(configured_secret) and secrets.compare_digest(
        provided_secret,
        configured_secret,
    )


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
    projects = [project.object for project in projects]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Victoriano Iman Santosa",
        "project_list": projects,
        "title_query": title_query,
    }
    return render(request, "project.html", context)


@require_http_methods(["GET", "POST"])
def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        if _has_valid_write_secret(request):
            form.save()
            messages.success(request, "Proyek baru berhasil ditambahkan!")
            return redirect("main:show_projects")

        form.add_error("secret", "Kode rahasia tidak valid.")

    context = {
        "name": "Victoriano Iman Santosa",
        "form": form,
    }
    return render(request, "projects_form.html", context)


@require_POST
def delete_project(request, id):
    if not _has_valid_write_secret(request):
        messages.error(request, "Kode rahasia tidak valid.")
        return redirect("main:show_projects")

    project = get_object_or_404(Project, pk=id)
    project.delete()
    messages.success(request, "Proyek berhasil dihapus!")
    return redirect("main:show_projects")


@require_GET
def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")


@require_GET
def show_json_by_id(request, id):
    project = get_object_or_404(Project, pk=id)
    data = serializers.serialize("json", [project])
    return HttpResponse(data, content_type="application/json")


@require_http_methods(["GET", "POST"])
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


@require_http_methods(["GET", "POST"])
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


@require_POST
def delete_blog(request, id):
    blog_post = get_object_or_404(BlogPost, pk=id)
    blog_post.delete()
    messages.success(request, "Blog berhasil dihapus!")
    return redirect("main:show_blog")


@require_GET
def get_blog_json(request):
    blog_posts = BlogPost.objects.order_by("-created_at", "-id")
    blog_posts_json = serializers.serialize("json", blog_posts)
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
    }
    return render(request, "blog.html", context)

