import json

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from main.models import BlogPost, Experience, Project


@override_settings(PORTFOLIO_WRITE_SECRET="test-write-secret")
class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

    def test_projects_json_endpoint_returns_all_projects(self):
        project = Project.objects.create(
            title="Portfolio Website",
            description="A Django portfolio website.",
            tech_stack="Django, Python",
        )

        response = self.client.get(reverse("main:get_projects_json"))
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(data[0]["pk"], str(project.pk))

    def test_projects_json_endpoint_filters_by_title(self):
        matching_project = Project.objects.create(
            title="Portfolio Website",
            description="A Django portfolio website.",
            tech_stack="Django, Python",
        )
        Project.objects.create(
            title="Unrelated Project",
            description="Another project.",
            tech_stack="Python",
        )

        response = self.client.get(reverse("main:get_projects_json"), {"title": "portfolio"})
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["pk"], str(matching_project.pk))

    def test_projects_page_uses_filtered_json_response(self):
        matching_project = Project.objects.create(
            title="Portfolio Website",
            description="A Django portfolio website.",
            tech_stack="Django, Python",
        )
        Project.objects.create(
            title="Unrelated Project",
            description="Another project.",
            tech_stack="Python",
        )

        response = self.client.get(
            reverse("main:show_projects"),
            {"title": "portfolio"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, matching_project.title)
        self.assertNotContains(response, "Unrelated Project")
        self.assertEqual(response.context["title_query"], "portfolio")
        self.assertContains(response, 'value="portfolio"')
        self.assertContains(response, 'name="title"')

    def test_delete_project_removes_project_and_redirects(self):
        project = Project.objects.create(
            title="Project to delete",
            description="This project will be removed.",
            tech_stack="Django",
        )

        response = self.client.post(
            reverse("main:delete_project", args=[project.id]),
            {"secret": "test-write-secret"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Project.objects.filter(pk=project.id).exists())
        self.assertContains(response, "Proyek berhasil dihapus!")

    def test_project_form_requires_write_secret(self):
        response = self.client.post(
            reverse("main:create_project"),
            {
                "title": "Protected project",
                "description": "This should not be saved without the secret.",
                "tech_stack": "Django",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Project.objects.filter(title="Protected project").exists())
        self.assertContains(response, "Kode rahasia tidak valid.")

    def test_project_form_accepts_write_secret_header(self):
        response = self.client.post(
            reverse("main:create_project"),
            {
                "title": "Protected project",
                "description": "This should be saved with the header.",
                "tech_stack": "Django",
            },
            HTTP_X_PORTFOLIO_WRITE_SECRET=settings.PORTFOLIO_WRITE_SECRET,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Project.objects.filter(title="Protected project").exists())

    def test_delete_project_rejects_get_requests(self):
        project = Project.objects.create(
            title="Project kept on get",
            description="GET must not delete this project.",
            tech_stack="Django",
        )

        response = self.client.get(
            reverse("main:delete_project", args=[project.id]),
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Project.objects.filter(pk=project.id).exists())

    def test_blog_page_is_accessible_and_uses_blog_template(self):
        response = self.client.get(reverse("main:show_blog"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog.html")
        self.assertContains(response, "Tambah Blog")

    def test_blog_form_page_is_accessible(self):
        response = self.client.get(reverse("main:create_blog"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog_form.html")
        self.assertContains(response, "Tambah Blog")
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_blog_form_saves_post_and_redirects(self):
        response = self.client.post(
            reverse("main:create_blog"),
            {
                "title": "A blog created from the form",
                "content": "This post was submitted without using the Admin.",
            },
            follow=True,
        )

        blog_post = BlogPost.objects.get(title="A blog created from the form")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, blog_post.content)
        self.assertContains(response, "Blog baru berhasil ditambahkan!")

    def test_blog_page_displays_stored_post_title_and_content(self):
        blog_post = BlogPost.objects.create(
            title="My first blog post",
            content="This is the content of my first blog post.",
        )

        response = self.client.get(reverse("main:show_blog"))

        self.assertContains(response, blog_post.title)
        self.assertContains(response, blog_post.content)

    def test_blog_posts_are_ordered_newest_first(self):
        older_post = BlogPost.objects.create(title="Older post", content="Older content")
        newer_post = BlogPost.objects.create(title="Newer post", content="Newer content")
        timestamp = timezone.now()
        BlogPost.objects.filter(pk__in=[older_post.pk, newer_post.pk]).update(created_at=timestamp)

        response = self.client.get(reverse("main:show_blog"))
        rendered_html = response.content.decode()

        self.assertLess(rendered_html.index(newer_post.title), rendered_html.index(older_post.title))

    def test_blog_content_preserves_line_breaks_and_escapes_html(self):
        BlogPost.objects.create(
            title="Plain text post",
            content="First line\nSecond line\n\n<strong>Not raw HTML</strong>",
        )

        response = self.client.get(reverse("main:show_blog"))

        self.assertContains(response, "First line<br>Second line")
        self.assertContains(response, "&lt;strong&gt;Not raw HTML&lt;/strong&gt;")
        self.assertNotContains(response, "<strong>Not raw HTML</strong>")

    def test_blog_nav_link_is_available_on_all_pages(self):
        for route_name in ("main:show_main", "main:show_experience", "main:show_blog"):
            response = self.client.get(reverse(route_name))

            self.assertContains(response, f'href="{reverse("main:show_blog")}"')

    def test_empty_blog_page_displays_empty_state(self):
        response = self.client.get(reverse("main:show_blog"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog.html")
        self.assertContains(response, "No blog posts have been added yet.")

    def test_blog_post_is_registered_in_default_admin(self):
        self.assertIn(BlogPost, admin.site._registry)

    def test_admin_created_blog_post_appears_on_blog_page(self):
        get_user_model().objects.create_superuser(
            username="blog-admin",
            email="blog-admin@example.com",
            password="test-password",
        )
        self.assertTrue(self.client.login(username="blog-admin", password="test-password"))

        response = self.client.post(
            reverse("admin:main_blogpost_add"),
            {
                "title": "Admin-created post",
                "content": "Content entered through Django Admin.",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, 302)
        blog_response = self.client.get(reverse("main:show_blog"))
        self.assertContains(blog_response, "Admin-created post")
        self.assertContains(blog_response, "Content entered through Django Admin.")
