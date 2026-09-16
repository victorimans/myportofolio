from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import BlogPostForm, ProjectForm
from main.models import BlogPost, Experience, Project


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


def show_experience(request):
    context = {
        "name": "Victoriano Iman Santosa",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


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


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")


def show_json_by_id(request, id):
    project = get_object_or_404(Project, pk=id)
    data = serializers.serialize("json", [project])
    return HttpResponse(data, content_type="application/json")


def create_blog(request):
    form = BlogPostForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Blog baru berhasil ditambahkan!")
        return redirect("main:show_blog")

    context = {
        "name": "Victoriano Iman Santosa",
        "form": form,
    }
    return render(request, "blog_form.html", context)


def show_blog(request):
    context = {
        "name": "Victoriano Iman Santosa",
        "blog_posts": BlogPost.objects.order_by("-created_at", "-id"),
    }
    return render(request, "blog.html", context)
