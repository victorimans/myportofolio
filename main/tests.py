import json
import uuid
from urllib.parse import parse_qs, urlsplit
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import serializers
from django.db import connection
from django.http import HttpResponse
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import BlogPost, Experience, Project


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

    def test_project_writes_require_superuser(self):
        project = Project.objects.create(
            title="Protected project", description="Keep this project.", tech_stack="Django"
        )
        add_url = reverse("main:create_project")
        delete_url = reverse("main:delete_project", args=[project.id])
        payload = {"title": "New project", "description": "New description", "tech_stack": "Django"}

        for url, method in ((add_url, "get"), (add_url, "post"), (delete_url, "post")):
            response = getattr(self.client, method)(url, payload if method == "post" else None)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, f"/login/?next={url}")

        user = get_user_model().objects.create_user(username="member", password="password")
        self.client.force_login(user)
        for url, method in ((add_url, "get"), (add_url, "post"), (delete_url, "post")):
            self.assertEqual(getattr(self.client, method)(url, payload).status_code, 403)
        self.assertFalse(Project.objects.filter(title="New project").exists())
        self.assertTrue(Project.objects.filter(pk=project.pk).exists())

        owner = get_user_model().objects.create_superuser(username="owner", password="password")
        self.client.force_login(owner)
        self.assertEqual(self.client.get(add_url).status_code, 200)
        self.assertEqual(self.client.post(add_url, payload).status_code, 302)
        self.assertTrue(Project.objects.filter(title="New project").exists())
        self.assertEqual(self.client.get(delete_url).status_code, 405)
        self.assertEqual(self.client.post(delete_url).status_code, 302)
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())

    def login_as_owner(self):
        owner = get_user_model().objects.create_superuser(
            username="owner", password="password"
        )
        self.client.force_login(owner)
        return owner

    def test_blog_page_is_accessible_and_uses_blog_template(self):
        response = self.client.get(reverse("main:show_blog"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog.html")
        self.assertNotContains(response, "Tambah Blog")

    def test_blog_form_page_is_accessible(self):
        self.login_as_owner()
        response = self.client.get(reverse("main:create_blog"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog_form.html")
        self.assertContains(response, "Tambah Blog")
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_blog_form_saves_post_and_redirects(self):
        self.login_as_owner()
        response = self.client.post(
            reverse("main:create_blog"),
            {
                "title": "A blog created from the form",
                "content": "This post was submitted without using the Admin.",
                "category": "ai",
            },
            follow=True,
        )

        blog_post = BlogPost.objects.get(title="A blog created from the form")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, blog_post.content)
        self.assertContains(response, "Blog baru berhasil ditambahkan!")

    def test_blog_form_renders_all_editable_fields(self):
        self.login_as_owner()
        response = self.client.get(reverse("main:create_blog"))

        for field_name in ("title", "content", "category", "picture_link"):
            self.assertContains(response, f'name="{field_name}"')
        self.assertNotContains(response, 'name="created_at"')
        self.assertNotContains(response, 'name="id"')

    def test_blog_update_form_prefills_and_updates_post(self):
        self.login_as_owner()
        blog_post = BlogPost.objects.create(
            title="Original title",
            content="Original content",
            category="career",
            picture_link="https://example.com/original.jpg",
        )
        response = self.client.get(reverse("main:update_blog", args=[blog_post.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog_form.html")
        self.assertContains(response, "Edit Blog")
        self.assertContains(response, f'action="{reverse("main:update_blog", args=[blog_post.id])}"')
        self.assertContains(response, 'value="Original title"')
        self.assertContains(response, "Original content")

        created_at = blog_post.created_at
        response = self.client.post(
            reverse("main:update_blog", args=[blog_post.id]),
            {
                "title": "Updated title",
                "content": "Updated content",
                "category": "dsa",
                "picture_link": "https://example.com/updated.jpg",
            },
            follow=True,
        )

        blog_post.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(blog_post.created_at, created_at)
        self.assertEqual(blog_post.title, "Updated title")
        self.assertEqual(blog_post.category, "dsa")
        self.assertEqual(blog_post.picture_link, "https://example.com/updated.jpg")
        self.assertContains(response, "Updated title")
        self.assertContains(response, "Blog berhasil diperbarui!")

    def test_delete_blog_removes_post_and_rejects_get(self):
        owner = self.login_as_owner()
        blog_post = BlogPost.objects.create(
            title="Blog to delete",
            content="This post should be removed.",
        )

        response = self.client.get(reverse("main:delete_blog", args=[blog_post.id]))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(BlogPost.objects.filter(pk=blog_post.id).exists())

        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(owner)
        response = csrf_client.post(
            reverse("main:delete_blog", args=[blog_post.id]),
            follow=True,
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(BlogPost.objects.filter(pk=blog_post.id).exists())

        response = csrf_client.get(reverse("main:show_blog"))
        csrf_token = response.cookies["csrftoken"].value
        response = csrf_client.post(
            reverse("main:delete_blog", args=[blog_post.id]),
            {"csrfmiddlewaretoken": csrf_token},
            HTTP_X_CSRFTOKEN=csrf_token,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(BlogPost.objects.filter(pk=blog_post.id).exists())
        self.assertContains(response, "Blog berhasil dihapus!")

    def test_blog_json_endpoint_returns_ordered_complete_data(self):
        older_post = BlogPost.objects.create(
            title="Older JSON blog",
            content="Older JSON content",
            category="career",
        )
        newer_post = BlogPost.objects.create(
            title="Newer JSON blog",
            content="Newer JSON content",
            category="web-development",
            picture_link="https://example.com/blog.jpg",
        )
        timestamp = timezone.now()
        BlogPost.objects.filter(pk__in=[older_post.pk, newer_post.pk]).update(created_at=timestamp)

        response = self.client.get(reverse("main:get_blog_json"))
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual([item["pk"] for item in data[:2]], [newer_post.pk, older_post.pk])
        self.assertEqual(data[0]["fields"]["title"], "Newer JSON blog")
        self.assertEqual(data[0]["fields"]["content"], "Newer JSON content")
        self.assertEqual(data[0]["fields"]["category"], "web-development")
        self.assertEqual(data[0]["fields"]["picture_link"], "https://example.com/blog.jpg")
        self.assertAlmostEqual(
            timezone.datetime.fromisoformat(data[0]["fields"]["created_at"].replace("Z", "+00:00")).timestamp(),
            newer_post.created_at.timestamp(),
            delta=0.001,
        )

    def test_blogpost_database_schema_contains_model_fields(self):
        column_names = {
            column.name
            for column in connection.introspection.get_table_description(
                connection.cursor(),
                BlogPost._meta.db_table,
            )
        }

        self.assertTrue({"title", "content", "category", "picture_link", "created_at"}.issubset(column_names))

    def test_blog_templates_use_one_root_document(self):
        self.login_as_owner()
        list_response = self.client.get(reverse("main:show_blog"))
        form_response = self.client.get(reverse("main:create_blog"))

        self.assertEqual(list_response.content.decode().count("<!DOCTYPE html>"), 1)
        self.assertEqual(form_response.content.decode().count("<!DOCTYPE html>"), 1)
        self.assertContains(list_response, 'href="/static/css/style.css"')
        self.assertContains(form_response, 'href="/static/css/style.css"')

    def test_blog_page_displays_category_and_picture(self):
        self.login_as_owner()
        blog_post = BlogPost.objects.create(
            title="A categorized post",
            content="Post content",
            category="ai",
            picture_link="https://example.com/ai.jpg",
        )

        response = self.client.get(reverse("main:show_blog"))

        self.assertContains(response, blog_post.title)
        self.assertContains(response, "AI")
        self.assertContains(response, blog_post.picture_link)
        expected_date = f"{blog_post.created_at.day} {blog_post.created_at.strftime('%B %Y')}"
        self.assertContains(response, expected_date)
        self.assertContains(response, f'alt="Gambar {blog_post.title}"')
        self.assertContains(response, f'aria-label="Edit blog: {blog_post.title}"')
        self.assertContains(response, f'aria-label="Delete blog: {blog_post.title}"')
        self.assertContains(response, reverse("main:update_blog", args=[blog_post.id]))
        self.assertContains(response, reverse("main:delete_blog", args=[blog_post.id]))

    def test_blog_page_renders_deserialized_json_objects(self):
        blog_post = BlogPost.objects.create(
            title="JSON-backed title",
            content="JSON-backed content",
            category="personal",
        )
        json_response = HttpResponse(
            serializers.serialize("json", [blog_post]),
            content_type="application/json",
        )

        with patch("main.views.get_blog_json", return_value=json_response) as get_blog_json:
            response = self.client.get(reverse("main:show_blog"))

        get_blog_json.assert_called_once()
        self.assertContains(response, "JSON-backed title")
        self.assertContains(response, "JSON-backed content")
        self.assertEqual(response.context["blog_posts"][0].__class__, BlogPost)

    def test_blog_writes_require_superuser(self):
        blog_post = BlogPost.objects.create(title="Protected", content="Keep this post.")
        add_url = reverse("main:create_blog")
        edit_url = reverse("main:update_blog", args=[blog_post.id])
        delete_url = reverse("main:delete_blog", args=[blog_post.id])
        payload = {"title": "Changed", "content": "Changed content", "category": "ai"}

        for url, method in ((add_url, "get"), (add_url, "post"), (edit_url, "get"), (edit_url, "post"), (delete_url, "post")):
            response = getattr(self.client, method)(url, payload if method == "post" else None)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, f"/login/?next={url}")

        user = get_user_model().objects.create_user(username="member", password="password")
        self.client.force_login(user)
        for url, method in ((add_url, "get"), (add_url, "post"), (edit_url, "get"), (edit_url, "post"), (delete_url, "post")):
            self.assertEqual(getattr(self.client, method)(url, payload if method == "post" else None).status_code, 403)
        blog_post.refresh_from_db()
        self.assertEqual(blog_post.title, "Protected")
        self.assertFalse(BlogPost.objects.filter(title="Changed").exists())

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
                "category": "ai",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, 302)
        blog_response = self.client.get(reverse("main:show_blog"))
        self.assertContains(blog_response, "Admin-created post")
        self.assertContains(blog_response, "Content entered through Django Admin.")


class AuthorizationAcceptanceTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Public project", description="Project description", tech_stack="Django"
        )
        self.post = BlogPost.objects.create(title="Public blog", content="Blog content")
        self.editor_group = Group.objects.create(name="Editor")
        self.member = get_user_model().objects.create_user(
            username="ordinary", password="password", email="ordinary@example.com"
        )
        self.editor = get_user_model().objects.create_user(username="editor", password="password")
        self.editor.groups.add(self.editor_group)
        self.owner = get_user_model().objects.create_superuser(username="owner", password="password")
        self.clients = {"anonymous": Client()}
        for role, user in (("member", self.member), ("editor", self.editor), ("owner", self.owner)):
            client = Client()
            client.force_login(user)
            self.clients[role] = client
        self.project_data = {
            "title": "Changed project", "description": "Changed description", "tech_stack": "Python",
            "project_url": "https://example.com/project", "project_image_url": "https://example.com/image.png",
        }
        self.blog_data = {
            "title": "Changed blog", "content": "Changed content", "category": "career",
            "picture_link": "https://example.com/blog.png",
        }

    def assert_login_next(self, response, destination):
        self.assertEqual(response.status_code, 302)
        parts = urlsplit(response.url)
        self.assertEqual(parts.path, reverse("main:login"))
        self.assertEqual(parse_qs(parts.query).get("next"), [destination])

    def test_public_lists_and_json_details_for_every_role(self):
        routes = (
            (reverse("main:show_projects"), self.project.title),
            (reverse("main:show_blog"), self.post.title),
            (reverse("main:get_projects_json"), self.project.title),
            (reverse("main:show_json_by_id", args=[self.project.pk]), self.project.title),
            (reverse("main:get_blog_json"), self.post.title),
            (reverse("main:show_blog_json_by_id", args=[self.post.pk]), self.post.title),
        )
        for role, client in self.clients.items():
            for url, title in routes:
                with self.subTest(role=role, url=url):
                    self.assertContains(client.get(url), title)
        self.assertEqual(self.clients["anonymous"].get(
            reverse("main:show_blog_json_by_id", args=[self.post.pk + 1000])
        ).status_code, 404)

    def test_project_detail_html_is_public(self):
        url = reverse("main:show_project_detail", args=[self.project.pk])
        for role, client in self.clients.items():
            with self.subTest(role=role):
                self.assertContains(client.get(url), self.project.title)

    def test_anonymous_actions_redirect_even_for_unsupported_methods(self):
        actions = (
            reverse("main:create_project"),
            reverse("main:update_project", args=[self.project.pk]),
            reverse("main:delete_project", args=[self.project.pk]),
            reverse("main:toggle_star", args=[self.project.pk]),
            reverse("main:create_blog"),
            reverse("main:update_blog", args=[self.post.pk]),
            reverse("main:delete_blog", args=[self.post.pk]),
        )
        for url in actions:
            for method in ("get", "post", "put"):
                with self.subTest(url=url, method=method):
                    self.assert_login_next(getattr(self.clients["anonymous"], method)(url), url)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(BlogPost.objects.count(), 1)
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_login_next_accepts_local_destination_and_rejects_external(self):
        login_url = reverse("main:login")
        destination = reverse("main:update_blog", args=[self.post.pk])
        for next_value, expected in (
            (destination, destination),
            ("https://evil.example/steal", reverse("main:show_main")),
            ("//evil.example/steal", reverse("main:show_main")),
        ):
            with self.subTest(next_value=next_value):
                client = Client()
                response = client.post(
                    f"{login_url}?next={next_value}",
                    {"username": self.editor.username, "password": "password", "next": next_value},
                )
                self.assertRedirects(response, expected, fetch_redirect_response=False)

    def test_role_authorization_and_method_precedence(self):
        actions = (
            (reverse("main:create_project"), self.project_data, {"owner"}),
            (reverse("main:update_project", args=[self.project.pk]), self.project_data, {"editor", "owner"}),
            (reverse("main:delete_project", args=[self.project.pk]), {}, {"owner"}),
            (reverse("main:create_blog"), self.blog_data, {"owner"}),
            (reverse("main:update_blog", args=[self.post.pk]), self.blog_data, {"editor", "owner"}),
            (reverse("main:delete_blog", args=[self.post.pk]), {}, {"owner"}),
        )
        for url, data, allowed in actions:
            for role in ("member", "editor", "owner"):
                if role in allowed:
                    continue
                for method in ("get", "post", "put"):
                    with self.subTest(url=url, role=role, method=method):
                        self.assertEqual(getattr(self.clients[role], method)(url, data).status_code, 403)
            for role in allowed:
                with self.subTest(url=url, role=role, method="put"):
                    self.assertEqual(self.clients[role].put(url, data).status_code, 405)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(BlogPost.objects.count(), 1)
        self.project.refresh_from_db()
        self.post.refresh_from_db()
        self.assertEqual(self.project.title, "Public project")
        self.assertEqual(self.post.title, "Public blog")

    def test_project_forms_crud_and_writable_fields(self):
        create = reverse("main:create_project")
        update = reverse("main:update_project", args=[self.project.pk])
        self.assertContains(self.clients["owner"].get(create), 'name="title"')
        self.assertContains(self.clients["editor"].get(update), "Public project")
        self.assertEqual(Project.objects.count(), 1)
        for url in (create, update):
            self.assertEqual(self.clients["owner"].put(url).status_code, 405)
        invalid = {**self.project_data, "title": ""}
        for client, url in ((self.clients["owner"], create), (self.clients["editor"], update)):
            response = client.post(url, invalid)
            self.assertEqual(response.status_code, 200)
            self.assertFormError(response.context["form"], "title", "This field is required.")
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Public project")
        self.project.starred_by.add(self.member)
        response = self.clients["editor"].post(update, {**self.project_data, "starred_by": self.editor.pk})
        self.assertRedirects(response, reverse("main:show_projects"))
        self.project.refresh_from_db()
        for field, value in self.project_data.items():
            self.assertEqual(getattr(self.project, field), value)
        self.assertEqual(list(self.project.starred_by.all()), [self.member])
        self.assertRedirects(self.clients["owner"].post(create, self.project_data), reverse("main:show_projects"))
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(self.clients["owner"].get(reverse("main:delete_project", args=[self.project.pk])).status_code, 405)
        self.assertRedirects(self.clients["owner"].post(reverse("main:delete_project", args=[self.project.pk])), reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_blog_forms_crud_and_server_managed_fields(self):
        create = reverse("main:create_blog")
        update = reverse("main:update_blog", args=[self.post.pk])
        self.assertContains(self.clients["owner"].get(create), 'name="title"')
        self.assertContains(self.clients["editor"].get(update), "Public blog")
        original_date = self.post.created_at
        original_pk = self.post.pk
        for url in (create, update):
            self.assertEqual(self.clients["owner"].put(url).status_code, 405)
        for client, url in ((self.clients["owner"], create), (self.clients["editor"], update)):
            response = client.post(url, {**self.blog_data, "title": ""})
            self.assertEqual(response.status_code, 200)
            self.assertFormError(response.context["form"], "title", "This field is required.")
        self.assertEqual(BlogPost.objects.count(), 1)
        self.assertRedirects(self.clients["editor"].post(update, {
            **self.blog_data, "id": 99999, "created_at": "2000-01-01T00:00:00Z"
        }), reverse("main:show_blog"))
        self.post.refresh_from_db()
        self.assertEqual(self.post.pk, original_pk)
        self.assertEqual(self.post.created_at, original_date)
        for field, value in self.blog_data.items():
            self.assertEqual(getattr(self.post, field), value)
        self.assertRedirects(self.clients["owner"].post(create, self.blog_data), reverse("main:show_blog"))
        self.assertEqual(BlogPost.objects.count(), 2)
        self.assertEqual(self.clients["owner"].get(reverse("main:delete_blog", args=[self.post.pk])).status_code, 405)
        self.assertRedirects(self.clients["owner"].post(reverse("main:delete_blog", args=[self.post.pk])), reverse("main:show_blog"))
        self.assertFalse(BlogPost.objects.filter(pk=self.post.pk).exists())

    def test_editor_membership_is_checked_on_every_request(self):
        for update, payload in (
            (reverse("main:update_project", args=[self.project.pk]), self.project_data),
            (reverse("main:update_blog", args=[self.post.pk]), self.blog_data),
        ):
            self.assertEqual(self.clients["member"].get(update).status_code, 403)
            self.member.groups.add(self.editor_group)
            self.assertEqual(self.clients["member"].get(update).status_code, 200)
            self.assertRedirects(self.clients["member"].post(update, payload),
                                 reverse("main:show_projects" if "projects" in update else "main:show_blog"))
            self.member.groups.remove(self.editor_group)
            self.assertEqual(self.clients["member"].get(update).status_code, 403)
            self.assertEqual(self.clients["member"].post(update, payload).status_code, 403)
        self.owner.groups.add(self.editor_group)
        self.assertEqual(self.clients["owner"].get(reverse("main:create_blog")).status_code, 200)
        self.owner.groups.remove(self.editor_group)
        self.assertEqual(self.clients["owner"].get(reverse("main:create_project")).status_code, 200)

    def test_unknown_ids_return_404(self):
        unknown_project = uuid.uuid4()
        for url in (
            reverse("main:update_project", args=[unknown_project]),
            reverse("main:delete_project", args=[unknown_project]),
            reverse("main:toggle_star", args=[unknown_project]),
            reverse("main:update_blog", args=[self.post.pk + 1000]),
            reverse("main:delete_blog", args=[self.post.pk + 1000]),
        ):
            with self.subTest(url=url):
                self.assertEqual(self.clients["owner"].post(url).status_code, 404)
        self.assertEqual(self.clients["anonymous"].get(
            reverse("main:show_json_by_id", args=[unknown_project])
        ).status_code, 404)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(BlogPost.objects.count(), 1)

    def test_star_toggle_is_post_only_independent_and_private(self):
        other = Project.objects.create(title="Other", description="Other description", tech_stack="Python")
        url = reverse("main:toggle_star", args=[self.project.pk])
        for role in ("member", "editor", "owner"):
            client = self.clients[role]
            user = {"member": self.member, "editor": self.editor, "owner": self.owner}[role]
            self.assertEqual(client.get(url).status_code, 405)
            self.assertEqual(client.put(url).status_code, 405)
            self.assertRedirects(client.post(url), reverse("main:show_projects"))
            self.assertEqual(self.project.starred_by.filter(pk=user.pk).count(), 1)
            self.assertEqual(other.starred_by.count(), 0)
            self.assertContains(client.get(reverse("main:show_projects")), "Unstar")
            self.assertRedirects(client.post(url), reverse("main:show_projects"))
            self.assertFalse(self.project.starred_by.filter(pk=user.pk).exists())
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_valid_csrf_star_toggle_and_zero_count(self):
        url = reverse("main:toggle_star", args=[self.project.pk])
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.member)
        page = client.get(reverse("main:show_projects"))
        self.assertContains(page, "star-count")
        self.assertContains(page, "0 stars")
        token = page.cookies["csrftoken"].value
        self.assertRedirects(client.post(url, {"csrfmiddlewaretoken": token}), reverse("main:show_projects"))
        self.assertEqual(self.project.starred_by.filter(pk=self.member.pk).count(), 1)
        self.assertRedirects(client.post(url, {"csrfmiddlewaretoken": token}), reverse("main:show_projects"))
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_project_json_never_exposes_star_membership(self):
        self.project.starred_by.add(self.member)
        for url in (reverse("main:get_projects_json"), reverse("main:show_json_by_id", args=[self.project.pk])):
            for client in self.clients.values():
                response = client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["Content-Type"], "application/json")
                records = json.loads(response.content)
                self.assertEqual(len(records), 1)
                self.assertEqual(records[0]["fields"]["title"], self.project.title)
                self.assertNotIn("starred_by", records[0]["fields"])
                for secret in (self.member.username, self.member.email, '"starred_by"'):
                    self.assertNotIn(secret, response.content.decode())
        self.assertEqual(len(json.loads(self.clients["anonymous"].get(
            reverse("main:get_projects_json"), {"title": "not-found"}
        ).content)), 0)

    def test_template_controls_match_roles_and_hide_identifying_stars(self):
        self.project.starred_by.add(self.member)
        for role, client in self.clients.items():
            project_page = client.get(reverse("main:show_projects"))
            blog_page = client.get(reverse("main:show_blog"))
            self.assertContains(project_page, self.project.title)
            self.assertContains(blog_page, self.post.title)
            self.assertContains(project_page, "star-count")
            self.assertNotContains(project_page, f"Dibintangi oleh {self.member.username}")
            self.assertNotContains(project_page, self.member.email)
            self.assertEqual("Tambah Project" in project_page.content.decode(), role == "owner")
            self.assertEqual("Hapus Project" in project_page.content.decode(), role == "owner")
            self.assertEqual("Edit Project" in project_page.content.decode(), role in ("editor", "owner"))
            self.assertEqual("Tambah Blog" in blog_page.content.decode(), role == "owner")
            self.assertEqual("Edit Blog" in blog_page.content.decode(), role in ("editor", "owner"))
            self.assertEqual("Hapus Blog" in blog_page.content.decode(), role == "owner")
            self.assertNotIn("star-form", blog_page.content.decode())
            self.assertNotIn("star-count", blog_page.content.decode())
            if role == "anonymous":
                self.assertNotContains(project_page, 'action="' + reverse("main:toggle_star", args=[self.project.pk]) + '"')
                self.assertContains(project_page, reverse("main:login"))
            else:
                self.assertContains(project_page, 'action="' + reverse("main:toggle_star", args=[self.project.pk]) + '"')
                self.assertContains(project_page, "csrfmiddlewaretoken")
        for client in self.clients.values():
            for url in (reverse("main:get_blog_json"), reverse("main:show_blog_json_by_id", args=[self.post.pk])):
                fields = json.loads(client.get(url).content)[0]["fields"]
                self.assertFalse(any("star" in key or "user" in key for key in fields))

    def test_csrf_rejects_all_mutations_without_token(self):
        for user, url, payload in (
            (self.owner, reverse("main:create_project"), self.project_data),
            (self.editor, reverse("main:update_project", args=[self.project.pk]), self.project_data),
            (self.owner, reverse("main:delete_project", args=[self.project.pk]), {}),
            (self.member, reverse("main:toggle_star", args=[self.project.pk]), {}),
            (self.owner, reverse("main:create_blog"), self.blog_data),
            (self.editor, reverse("main:update_blog", args=[self.post.pk]), self.blog_data),
            (self.owner, reverse("main:delete_blog", args=[self.post.pk]), {}),
        ):
            with self.subTest(url=url):
                client = Client(enforce_csrf_checks=True)
                client.force_login(user)
                self.assertEqual(client.post(url, payload).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(BlogPost.objects.count(), 1)
        self.assertEqual(self.project.starred_by.count(), 0)
        self.project.refresh_from_db()
        self.post.refresh_from_db()
        self.assertEqual(self.project.title, "Public project")
        self.assertEqual(self.post.title, "Public blog")
