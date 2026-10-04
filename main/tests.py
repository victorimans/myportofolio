import json
import re
import uuid
from datetime import timedelta
from urllib.parse import parse_qs, urlsplit
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import connection
from django.http import JsonResponse
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from main.forms import BlogPostForm
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

    def test_projects_page_loads_projects_through_ajax(self):
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
        self.assertNotContains(response, matching_project.title)
        self.assertNotContains(response, "Unrelated Project")
        self.assertEqual(response.context["title_query"], "portfolio")
        self.assertContains(response, 'value="portfolio"')
        self.assertContains(response, 'id="project-search-form"')
        self.assertContains(response, 'id="project-grid"')
        self.assertContains(response, reverse("main:get_projects_json"))

    def test_projects_json_includes_star_count_and_current_users_star_state(self):
        project = Project.objects.create(
            title="Starred project",
            description="A project with private star membership.",
            tech_stack="Django",
        )
        owner = get_user_model().objects.create_user(username="star-owner", password="password")
        other_user = get_user_model().objects.create_user(username="star-other", password="password")
        project.starred_by.add(owner)

        owner_client = Client()
        owner_client.force_login(owner)
        for client, expected_starred in ((self.client, False), (owner_client, True)):
            with self.subTest(is_starred=expected_starred):
                response = client.get(reverse("main:get_projects_json"))
                data = json.loads(response.content)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(data), 1)
                self.assertEqual(data[0]["pk"], str(project.pk))
                self.assertEqual(data[0]["fields"]["star_count"], 1)
                self.assertEqual(data[0]["fields"]["is_starred"], expected_starred)
                self.assertNotIn("starred_by_names", data[0]["fields"])
                self.assertNotIn(owner.username, response.content.decode())
                self.assertNotIn(other_user.username, response.content.decode())

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
        self.assertNotContains(response, blog_post.content)
        self.assertEqual(blog_post.content, "This post was submitted without using the Admin.")
        self.assertEqual(blog_post.category, "ai")
        self.assertRedirects(response, reverse("main:show_blog"))
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
        self.assertEqual(blog_post.content, "Updated content")
        self.assertNotContains(response, blog_post.title)
        self.assertRedirects(response, reverse("main:show_blog"))
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
        newest_post = BlogPost.objects.create(title="Newest JSON blog", content="Newest content")
        BlogPost.objects.filter(pk=newest_post.pk).update(created_at=timestamp + timedelta(days=1))
        newer_post.refresh_from_db()

        with patch("main.views.serializers.serialize", side_effect=AssertionError("Listing must use manual JSON")):
            response = self.client.get(reverse("main:get_blog_json"))
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIsInstance(data, list)
        self.assertEqual([item["pk"] for item in data], [newest_post.pk, newer_post.pk, older_post.pk])
        for item in data:
            self.assertIs(type(item["pk"]), int)
            self.assertEqual(set(item), {"pk", "fields"})
            self.assertEqual(set(item["fields"]), {
                "title", "content", "category", "picture_link", "created_at",
                "category_display", "star_count", "is_starred",
            })
            self.assertIs(type(item["fields"]["star_count"]), int)
            self.assertIs(item["fields"]["is_starred"], False)
            self.assertEqual(item["fields"]["star_count"], 0)
        fields = data[1]["fields"]
        self.assertEqual(fields["title"], newer_post.title)
        self.assertEqual(fields["content"], newer_post.content)
        self.assertEqual(fields["category"], newer_post.category)
        self.assertEqual(fields["category_display"], newer_post.get_category_display())
        self.assertEqual(fields["picture_link"], newer_post.picture_link)
        self.assertEqual(
            timezone.datetime.fromisoformat(fields["created_at"].replace("Z", "+00:00")),
            newer_post.created_at,
        )

    def test_blog_json_search_matches_partial_case_insensitive_titles_not_content(self):
        matching_post = BlogPost.objects.create(
            title="Learning Django with AJAX",
            content="A title search result.",
        )
        BlogPost.objects.create(
            title="Unrelated writing",
            content="Learning Django with AJAX appears only in the body.",
        )

        for title_query in ("django", "DJANGO", "arning dJanGo with"):
            with self.subTest(title_query=title_query):
                response = self.client.get(reverse("main:get_blog_json"), {"title": title_query})

                self.assertEqual(response.status_code, 200)
                self.assertEqual([item["pk"] for item in response.json()], [matching_post.pk])
                self.assertEqual(response.json()[0]["fields"]["title"], matching_post.title)

    def test_blog_json_search_trims_surrounding_whitespace(self):
        matching_post = BlogPost.objects.create(title="Django notes", content="Matching content")
        BlogPost.objects.create(title="Other notes", content="Unrelated content")

        response = self.client.get(reverse("main:get_blog_json"), {"title": " \tDjango\n "})

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["pk"] for item in response.json()], [matching_post.pk])

    def test_blog_json_missing_empty_and_whitespace_search_return_all_posts(self):
        older_post = BlogPost.objects.create(title="Older writing", content="Older content")
        newer_post = BlogPost.objects.create(title="Newer writing", content="Newer content")
        BlogPost.objects.filter(pk__in=[older_post.pk, newer_post.pk]).update(created_at=timezone.now())

        for params in ({}, {"title": ""}, {"title": " \t\n "}):
            with self.subTest(params=params):
                response = self.client.get(reverse("main:get_blog_json"), params)

                self.assertEqual(response.status_code, 200)
                self.assertEqual([item["pk"] for item in response.json()], [newer_post.pk, older_post.pk])

    def test_blog_json_search_without_matches_returns_empty_list(self):
        BlogPost.objects.create(title="Existing writing", content="Existing content")

        response = self.client.get(reverse("main:get_blog_json"), {"title": "not-found"})

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json(), [])

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

    def test_blog_json_returns_category_display_and_picture(self):
        blog_post = BlogPost.objects.create(
            title="A categorized post",
            content="Post content",
            category="ai",
            picture_link="https://example.com/ai.jpg",
        )

        response = self.client.get(reverse("main:get_blog_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["fields"]["category_display"], "AI")
        self.assertEqual(response.json()[0]["fields"]["picture_link"], blog_post.picture_link)

    def test_blog_shell_does_not_load_collection_or_call_json_endpoint(self):
        blog_post = BlogPost.objects.create(
            title="JSON-backed title",
            content="JSON-backed content",
            category="personal",
        )
        self.login_as_owner()
        anonymous_client = Client()
        for client in (anonymous_client, self.client):
            with self.subTest(authenticated=client == self.client):
                with patch("main.views.get_blog_json") as get_blog_json:
                    with CaptureQueriesContext(connection) as queries:
                        response = client.get(reverse("main:show_blog"))

                get_blog_json.assert_not_called()
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, "blog.html")
                self.assertNotIn("blog_posts", response.context)
                self.assertNotContains(response, blog_post.title)
                self.assertNotContains(response, blog_post.content)
                self.assertFalse(any(
                    BlogPost._meta.db_table.lower() in query["sql"].lower()
                    for query in queries.captured_queries
                ))

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

    def test_blog_json_returns_stored_post_title_and_content(self):
        blog_post = BlogPost.objects.create(
            title="My first blog post",
            content="This is the content of my first blog post.",
        )

        response = self.client.get(reverse("main:get_blog_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["fields"]["title"], blog_post.title)
        self.assertEqual(response.json()[0]["fields"]["content"], blog_post.content)

    def test_blog_posts_are_ordered_newest_first(self):
        older_post = BlogPost.objects.create(title="Older post", content="Older content")
        newer_post = BlogPost.objects.create(title="Newer post", content="Newer content")
        timestamp = timezone.now()
        BlogPost.objects.filter(pk=older_post.pk).update(created_at=timestamp)
        BlogPost.objects.filter(pk=newer_post.pk).update(created_at=timestamp - timedelta(days=1))

        response = self.client.get(reverse("main:get_blog_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["pk"] for item in response.json()], [older_post.pk, newer_post.pk])

    def test_blog_json_preserves_line_breaks_and_markup_as_data(self):
        blog_post = BlogPost.objects.create(
            title="Plain text post",
            content="First line\nSecond line\n\n<strong>Not raw HTML</strong>",
        )

        response = self.client.get(reverse("main:get_blog_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["fields"]["content"], blog_post.content)
        shell_response = self.client.get(reverse("main:show_blog"))
        self.assertNotContains(shell_response, "<strong>Not raw HTML</strong>")

    def test_blog_nav_link_is_available_on_all_pages(self):
        for route_name in ("main:show_main", "main:show_experience", "main:show_blog"):
            response = self.client.get(reverse(route_name))

            self.assertContains(response, f'href="{reverse("main:show_blog")}"')

    def test_empty_blog_json_returns_empty_list(self):
        response = self.client.get(reverse("main:get_blog_json"))

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.json(), [])

    def test_blog_post_is_registered_in_default_admin(self):
        self.assertIn(BlogPost, admin.site._registry)

    def test_admin_created_blog_post_appears_in_blog_json(self):
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
        blog_response = self.client.get(reverse("main:get_blog_json"))
        self.assertEqual(blog_response.status_code, 200)
        self.assertEqual(blog_response.json()[0]["fields"]["title"], "Admin-created post")
        self.assertEqual(blog_response.json()[0]["fields"]["content"], "Content entered through Django Admin.")


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
                    response = client.get(url)
                    if url == reverse("main:show_projects"):
                        self.assertContains(response, 'id="project-grid"')
                        self.assertNotContains(response, title)
                    elif url == reverse("main:show_blog"):
                        self.assertEqual(response.status_code, 200)
                        self.assertTemplateUsed(response, "blog.html")
                        self.assertNotContains(response, title)
                        self.assertNotIn("blog_posts", response.context)
                    else:
                        self.assertContains(response, title)
        self.assertEqual(self.clients["anonymous"].get(
            reverse("main:show_blog_json_by_id", args=[self.post.pk + 1000])
        ).status_code, 404)

    def test_blog_title_search_preserves_order_star_state_and_privacy_for_every_role(self):
        self.post.starred_by.add(self.member, self.editor)
        tied_post = BlogPost.objects.create(title="Another PUBLIC blog", content="Another result")
        newest_post = BlogPost.objects.create(title="Newest public blog", content="Newest result")
        BlogPost.objects.create(title="Unrelated title", content="Public appears only in the body")
        timestamp = timezone.now()
        BlogPost.objects.filter(pk__in=[self.post.pk, tied_post.pk]).update(created_at=timestamp)
        BlogPost.objects.filter(pk=newest_post.pk).update(created_at=timestamp + timedelta(days=1))

        for role, client in self.clients.items():
            with self.subTest(role=role):
                response = client.get(reverse("main:get_blog_json"), {"title": "  pUbLiC  "})
                data = response.json()

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["Content-Type"], "application/json")
                self.assertEqual([item["pk"] for item in data], [newest_post.pk, tied_post.pk, self.post.pk])
                for item in data:
                    self.assertIs(type(item["pk"]), int)
                    self.assertEqual(set(item), {"pk", "fields"})
                    self.assertEqual(set(item["fields"]), {
                        "title", "content", "category", "picture_link", "created_at",
                        "category_display", "star_count", "is_starred",
                    })
                    self.assertEqual(item["fields"]["star_count"], 2 if item["pk"] == self.post.pk else 0)
                    self.assertIs(
                        item["fields"]["is_starred"],
                        item["pk"] == self.post.pk and role in ("member", "editor"),
                    )
                for user in (self.member, self.editor, self.owner):
                    self.assertNotIn(user.username, response.content.decode())
                    if user.email:
                        self.assertNotIn(user.email, response.content.decode())

    def test_blog_search_shell_preserves_escaped_query_and_controls_for_every_role(self):
        title_query = '\"><script>alert(1)</script>&'
        escaped_query = '&quot;&gt;&lt;script&gt;alert(1)&lt;/script&gt;&amp;'

        for role, client in self.clients.items():
            with self.subTest(role=role):
                with patch("main.views.get_blog_json") as get_blog_json:
                    with CaptureQueriesContext(connection) as queries:
                        response = client.get(reverse("main:show_blog"), {"title": f"  {title_query}  "})

                get_blog_json.assert_not_called()
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, "blog.html")
                self.assertEqual(response.context["title_query"], title_query)
                self.assertContains(response, f'value="{escaped_query}"')
                self.assertNotContains(response, title_query)
                self.assertContains(response, 'id="blog-search-form"')
                self.assertContains(response, 'id="blog-search-input"')
                self.assertContains(response, 'name="title"')
                self.assertContains(response, 'type="search"')
                self.assertContains(response, 'id="blog-list"')
                self.assertContains(response, f'data-json-url="{reverse("main:get_blog_json")}"')
                self.assertContains(response, 'src="/static/js/blog.js"')
                self.assertNotIn("blog_posts", response.context)
                self.assertNotContains(response, self.post.title)
                self.assertNotContains(response, self.post.content)
                self.assertFalse(any(
                    BlogPost._meta.db_table.lower() in query["sql"].lower()
                    for query in queries.captured_queries
                ))

    def test_project_detail_html_is_public(self):
        url = reverse("main:show_project_detail", args=[self.project.pk])
        for role, client in self.clients.items():
            with self.subTest(role=role):
                response = client.get(url)
                self.assertContains(response, self.project.title)
                self.assertNotContains(response, 'popovertarget="add-project-modal"')

    def test_add_blog_modal_is_available_only_to_superuser(self):
        create_url = reverse("main:create_blog_ajax")
        self.assertEqual(create_url, "/blog/add-ajax/")
        for role, client in self.clients.items():
            with self.subTest(role=role):
                response = client.get(reverse("main:show_blog"))
                self.assertEqual(response.status_code, 200)
                if role == "owner":
                    self.assertContains(response, 'popovertarget="add-blog-modal"')
                    self.assertContains(response, 'id="add-blog-modal"')
                    self.assertContains(response, 'id="blog-form"')
                    form_match = re.search(
                        r'<form\b(?=[^>]*\bid="blog-form")[^>]*>.*?</form>',
                        response.content.decode(),
                        re.DOTALL,
                    )
                    self.assertIsNotNone(form_match)
                    form_html = form_match.group()
                    self.assertIn(f'action="{create_url}"', form_html)
                    self.assertRegex(form_html, r'method="(?i:post)"')
                    self.assertIn('name="csrfmiddlewaretoken"', form_html)
                    for field_name in BlogPostForm().fields:
                        self.assertIn(f'name="{field_name}"', form_html)
                    for field_name in ("id", "pk", "created_at", "starred_by"):
                        self.assertNotIn(f'name="{field_name}"', form_html)
                else:
                    self.assertNotContains(response, 'id="add-blog-modal"')
                    self.assertNotContains(response, 'popovertarget="add-blog-modal"')
                    self.assertNotContains(response, 'id="blog-form"')
                    self.assertNotContains(response, "Tambah Blog")

    def test_blog_ajax_create_persists_post_and_exposes_it_in_public_search(self):
        response = self.clients["owner"].post(reverse("main:create_blog_ajax"), self.blog_data)

        self.assertEqual(response.status_code, 201)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response["Content-Type"], "application/json")
        payload = response.json()
        self.assertIs(type(payload["pk"]), int)
        blog_post = BlogPost.objects.get(pk=payload["pk"])
        self.assertEqual(payload, {
            "message": "Blog berhasil ditambahkan.",
            "pk": blog_post.pk,
        })
        self.assertEqual(BlogPost.objects.count(), 2)
        for field_name, value in self.blog_data.items():
            self.assertEqual(getattr(blog_post, field_name), value)
        for params in ({}, {"title": "  CHANGED  "}):
            with self.subTest(params=params):
                listing = self.clients["anonymous"].get(reverse("main:get_blog_json"), params)
                self.assertEqual(listing.status_code, 200)
                records = listing.json()
                record = next(item for item in records if item["pk"] == blog_post.pk)
                for field_name, value in self.blog_data.items():
                    self.assertEqual(record["fields"][field_name], value)
                if params:
                    self.assertEqual([item["pk"] for item in records], [blog_post.pk])

    def test_blog_ajax_create_returns_form_errors_without_mutation(self):
        original_posts = list(BlogPost.objects.values())
        cases = (
            ("title", None, "required"),
            ("content", None, "required"),
            ("title", "", "required"),
            ("content", "", "required"),
            ("category", "not-a-category", "invalid_choice"),
            ("picture_link", "not-a-url", "invalid"),
        )
        for field_name, value, code in cases:
            with self.subTest(field_name=field_name, value=value):
                data = self.blog_data.copy()
                if value is None:
                    data.pop(field_name)
                else:
                    data[field_name] = value
                form = BlogPostForm(data)
                self.assertFalse(form.is_valid())
                response = self.clients["owner"].post(reverse("main:create_blog_ajax"), data)

                self.assertEqual(response.status_code, 400)
                self.assertIsInstance(response, JsonResponse)
                self.assertEqual(response["Content-Type"], "application/json")
                self.assertEqual(response.json(), {"errors": form.errors.get_json_data()})
                self.assertEqual(response.json()["errors"][field_name][0]["code"], code)
                self.assertEqual(list(BlogPost.objects.values()), original_posts)

    def test_blog_ajax_create_rejects_non_superusers_with_json(self):
        original_posts = list(BlogPost.objects.values())
        for role in ("anonymous", "member", "editor"):
            with self.subTest(role=role):
                response = self.clients[role].post(reverse("main:create_blog_ajax"), self.blog_data)

                self.assertEqual(response.status_code, 403)
                self.assertIsInstance(response, JsonResponse)
                self.assertEqual(response["Content-Type"], "application/json")
                self.assertIn("message", response.json())
                self.assertEqual(list(BlogPost.objects.values()), original_posts)

    def test_blog_ajax_create_rechecks_revoked_superuser_permission(self):
        self.assertContains(
            self.clients["owner"].get(reverse("main:show_blog")),
            'id="add-blog-modal"',
        )
        self.owner.groups.add(self.editor_group)
        get_user_model().objects.filter(pk=self.owner.pk).update(is_superuser=False)
        original_posts = list(BlogPost.objects.values())

        response = self.clients["owner"].post(reverse("main:create_blog_ajax"), self.blog_data)

        self.assertEqual(response.status_code, 403)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("message", response.json())
        self.assertEqual(list(BlogPost.objects.values()), original_posts)
        page = self.clients["owner"].get(reverse("main:show_blog"))
        self.assertNotContains(page, 'id="add-blog-modal"')
        self.assertNotContains(page, 'popovertarget="add-blog-modal"')

    def test_blog_ajax_create_is_post_only(self):
        url = reverse("main:create_blog_ajax")
        original_posts = list(BlogPost.objects.values())
        for role, client in self.clients.items():
            for method in ("get", "head", "put", "patch", "delete", "options"):
                with self.subTest(role=role, method=method):
                    response = getattr(client, method)(url)
                    self.assertEqual(response.status_code, 405)
                    self.assertEqual(response["Allow"], "POST")
                    self.assertEqual(list(BlogPost.objects.values()), original_posts)

    def test_blog_ajax_create_requires_csrf_and_accepts_modal_form_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        url = reverse("main:create_blog_ajax")
        original_posts = list(BlogPost.objects.values())
        self.assertEqual(client.post(url, self.blog_data).status_code, 403)
        self.assertEqual(list(BlogPost.objects.values()), original_posts)
        page = client.get(reverse("main:show_blog"))
        self.assertEqual(page.status_code, 200)
        form_match = re.search(
            r'<form\b(?=[^>]*\bid="blog-form")[^>]*>.*?</form>',
            page.content.decode(),
            re.DOTALL,
        )
        self.assertIsNotNone(form_match)
        token_match = re.search(
            r'<input\b(?=[^>]*\bname="csrfmiddlewaretoken")[^>]*\bvalue="([^"]+)"',
            form_match.group(),
        )
        self.assertIsNotNone(token_match)
        self.assertEqual(client.post(url, self.blog_data).status_code, 403)
        self.assertEqual(list(BlogPost.objects.values()), original_posts)

        response = client.post(url, {
            **self.blog_data,
            "csrfmiddlewaretoken": token_match.group(1),
        })

        self.assertEqual(response.status_code, 201)
        self.assertTrue(BlogPost.objects.filter(pk=response.json()["pk"], **self.blog_data).exists())
        self.assertEqual(BlogPost.objects.count(), 2)

    def test_blog_ajax_create_ignores_server_managed_fields(self):
        self.post.starred_by.add(self.member)
        original_post = BlogPost.objects.values().get(pk=self.post.pk)
        before_create = timezone.now()
        response = self.clients["owner"].post(reverse("main:create_blog_ajax"), {
            **self.blog_data,
            "id": self.post.pk,
            "pk": 99999,
            "created_at": "2000-01-01T00:00:00Z",
            "starred_by": [self.member.pk, self.editor.pk],
        })
        after_create = timezone.now()

        self.assertEqual(response.status_code, 201)
        blog_post = BlogPost.objects.get(pk=response.json()["pk"])
        self.assertIs(type(blog_post.pk), int)
        self.assertNotIn(blog_post.pk, (self.post.pk, 99999))
        self.assertGreaterEqual(blog_post.created_at, before_create)
        self.assertLessEqual(blog_post.created_at, after_create)
        self.assertFalse(blog_post.starred_by.exists())
        for field_name, value in self.blog_data.items():
            self.assertEqual(getattr(blog_post, field_name), value)
        self.assertEqual(BlogPost.objects.count(), 2)
        self.assertEqual(BlogPost.objects.values().get(pk=self.post.pk), original_post)
        self.assertEqual(list(self.post.starred_by.all()), [self.member])

    def test_add_project_modal_is_available_only_to_superuser(self):
        create_url = reverse("main:create_project_ajax")
        for role, client in self.clients.items():
            with self.subTest(role=role):
                response = client.get(reverse("main:show_projects"))
                if role == "owner":
                    self.assertContains(response, 'popovertarget="add-project-modal"')
                    self.assertContains(response, 'id="add-project-modal"')
                    self.assertContains(response, f'action="{create_url}"')
                    self.assertContains(response, 'name="csrfmiddlewaretoken"')
                    for field_name in (
                        "title",
                        "description",
                        "tech_stack",
                        "project_url",
                        "project_image_url",
                    ):
                        self.assertContains(response, f'name="{field_name}"')
                else:
                    self.assertNotContains(response, 'id="add-project-modal"')
                    self.assertNotContains(response, 'popovertarget="add-project-modal"')

    def test_project_ajax_create_returns_created_project(self):
        response = self.clients["owner"].post(reverse("main:create_project_ajax"), {
            "title": "AJAX-created project",
            "description": "Created without a page reload.",
            "tech_stack": "Django",
            "project_url": "https://example.com/project",
            "project_image_url": "https://example.com/project.jpg",
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response["Content-Type"], "application/json")
        payload = json.loads(response.content)
        project = Project.objects.get(title="AJAX-created project")
        self.assertEqual(payload, {
            "message": "Proyek berhasil ditambahkan.",
            "pk": str(project.pk),
        })

    def test_project_ajax_create_returns_model_form_validation_errors(self):
        response = self.clients["owner"].post(reverse("main:create_project_ajax"), {
            "title": "",
            "description": "Missing title",
            "tech_stack": "Django",
            "project_url": "javascript:alert(1)",
        })

        self.assertEqual(response.status_code, 400)
        payload = json.loads(response.content)
        self.assertEqual(payload["errors"]["title"][0]["code"], "required")
        self.assertEqual(payload["errors"]["project_url"][0]["code"], "invalid")
        self.assertEqual(Project.objects.count(), 1)

    def test_project_ajax_rejects_title_containing_only_html_tags(self):
        response = self.clients["owner"].post(reverse("main:create_project_ajax"), {
            "title": '<img src="x" onerror="alert(1)">',
            "description": "A project description",
            "tech_stack": "Django",
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["errors"]["title"][0]["message"],
            "Nama proyek tidak boleh hanya berisi tag HTML.",
        )
        self.assertEqual(Project.objects.count(), 1)

    def test_project_ajax_create_removes_markup_from_project_text(self):
        response = self.clients["owner"].post(reverse("main:create_project_ajax"), {
            "title": "Halo <b>dunia</b>",
            "description": "Membangun <em>website</em>",
            "tech_stack": "<strong>Django</strong> dan Python",
        })

        self.assertEqual(response.status_code, 201)
        project = Project.objects.get(pk=response.json()["pk"])
        self.assertEqual(project.title, "Halo dunia")
        self.assertEqual(project.description, "Membangun website")
        self.assertEqual(project.tech_stack, "Django dan Python")

    def test_project_form_page_uses_same_title_validation(self):
        response = self.clients["owner"].post(reverse("main:create_project"), {
            "title": "<b></b>",
            "description": "A project description",
            "tech_stack": "Django",
        })

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "title",
            "Nama proyek tidak boleh hanya berisi tag HTML.",
        )
        self.assertEqual(Project.objects.count(), 1)

    def test_existing_project_markup_is_returned_as_data(self):
        legacy = Project.objects.create(
            title='<img src="x" onerror="alert(1)">',
            description="Stored before validation was added.",
            tech_stack="Django",
        )

        response = self.clients["anonymous"].get(reverse("main:get_projects_json"))

        self.assertEqual(response.status_code, 200)
        record = next(item for item in response.json() if item["pk"] == str(legacy.pk))
        self.assertEqual(record["fields"]["title"], legacy.title)

    def test_project_ajax_create_rejects_non_superusers_with_json(self):
        url = reverse("main:create_project_ajax")
        for role in ("anonymous", "member", "editor"):
            with self.subTest(role=role):
                response = self.clients[role].post(url, {"title": "Not allowed"})
                self.assertEqual(response.status_code, 403)
                self.assertEqual(response["Content-Type"], "application/json")
                self.assertIn("message", json.loads(response.content))
        self.assertEqual(Project.objects.count(), 1)

    def test_project_ajax_create_is_post_only_and_requires_csrf(self):
        url = reverse("main:create_project_ajax")
        self.assertEqual(self.clients["owner"].get(url).status_code, 405)

        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        page = client.get(reverse("main:show_projects"))
        csrf_token = page.cookies["csrftoken"].value
        payload = {
            "title": "CSRF-protected project",
            "description": "Submitted with CSRF token.",
            "tech_stack": "Django",
        }
        self.assertEqual(client.post(url, payload).status_code, 403)
        response = client.post(url, {**payload, "csrfmiddlewaretoken": csrf_token})
        self.assertEqual(response.status_code, 201)

    def test_project_modal_posts_ajax_and_loads_ajax_script(self):
        response = self.clients["owner"].get(reverse("main:show_projects"))

        self.assertContains(response, f'action="{reverse("main:create_project_ajax")}"')
        self.assertContains(response, 'id="project-form"')
        self.assertContains(response, 'src="/static/js/projects.js"')
        self.assertContains(response, f'data-create-url="{reverse("main:create_project_ajax")}"')

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
            data = json.loads(client.get(reverse("main:get_projects_json")).content)
            self.assertTrue(next(item for item in data if item["pk"] == str(self.project.pk))["fields"]["is_starred"])
            self.assertRedirects(client.post(url), reverse("main:show_projects"))
            self.assertFalse(self.project.starred_by.filter(pk=user.pk).exists())
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_blog_star_toggle_is_post_only_and_independent(self):
        url = reverse("main:toggle_blog_star", args=[self.post.pk])
        for role in ("member", "editor", "owner"):
            client = self.clients[role]
            user = {"member": self.member, "editor": self.editor, "owner": self.owner}[role]
            self.assertEqual(client.get(url).status_code, 405)
            self.assertEqual(client.put(url).status_code, 405)
            self.assertRedirects(client.post(url), reverse("main:show_blog"))
            self.assertEqual(self.post.starred_by.filter(pk=user.pk).count(), 1)
            self.assertEqual(self.project.starred_by.count(), 0)
            fields = client.get(reverse("main:get_blog_json")).json()[0]["fields"]
            self.assertIs(fields["is_starred"], True)
            self.assertEqual(fields["star_count"], 1)
            self.assertRedirects(client.post(url), reverse("main:show_blog"))
            self.assertFalse(self.post.starred_by.filter(pk=user.pk).exists())
            fields = client.get(reverse("main:get_blog_json")).json()[0]["fields"]
            self.assertIs(fields["is_starred"], False)
            self.assertEqual(fields["star_count"], 0)
        self.assertEqual(self.post.starred_by.count(), 0)

    def test_valid_csrf_star_toggle_and_zero_count(self):
        url = reverse("main:toggle_star", args=[self.project.pk])
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.member)
        page = client.get(reverse("main:show_projects"))
        self.assertContains(page, 'id="project-grid"')
        data = json.loads(client.get(reverse("main:get_projects_json")).content)
        self.assertEqual(data[0]["fields"]["star_count"], 0)
        token = page.cookies["csrftoken"].value
        self.assertRedirects(client.post(url, {"csrfmiddlewaretoken": token}), reverse("main:show_projects"))
        self.assertEqual(self.project.starred_by.filter(pk=self.member.pk).count(), 1)
        self.assertRedirects(client.post(url, {"csrfmiddlewaretoken": token}), reverse("main:show_projects"))
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_blog_star_toggle_requires_valid_csrf_token(self):
        url = reverse("main:toggle_blog_star", args=[self.post.pk])
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.member)
        page = client.get(reverse("main:show_blog"))
        self.assertEqual(page.status_code, 200)
        fields = client.get(reverse("main:get_blog_json")).json()[0]["fields"]
        self.assertEqual(fields["star_count"], 0)
        self.assertIs(fields["is_starred"], False)
        token = page.cookies["csrftoken"].value
        self.assertRedirects(client.post(url, {"csrfmiddlewaretoken": token}), reverse("main:show_blog"))
        self.assertEqual(self.post.starred_by.filter(pk=self.member.pk).count(), 1)
        self.assertRedirects(client.post(url, {"csrfmiddlewaretoken": token}), reverse("main:show_blog"))
        self.assertEqual(self.post.starred_by.count(), 0)

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
            self.assertContains(project_page, 'id="project-grid"')
            self.assertNotContains(project_page, self.project.title)
            self.assertNotContains(blog_page, self.post.title)
            self.assertNotIn("blog_posts", blog_page.context)
            self.assertNotContains(project_page, f"Dibintangi oleh {self.member.username}")
            self.assertNotContains(project_page, self.member.email)
            self.assertEqual("Tambah Proyek" in project_page.content.decode(), role == "owner")
            self.assertEqual(project_page.context["can_edit"], role in ("editor", "owner"))
            project_json = json.loads(client.get(reverse("main:get_projects_json")).content)
            self.assertEqual(project_json[0]["fields"]["title"], self.project.title)
            self.assertEqual(project_json[0]["fields"]["star_count"], 1)
            self.assertEqual(project_json[0]["fields"]["is_starred"], role == "member")
            self.assertEqual("Tambah Blog" in blog_page.content.decode(), role == "owner")
            self.assertEqual(blog_page.context["can_edit"], role in ("editor", "owner"))
            self.assertNotContains(blog_page, f"Dibintangi oleh {self.member.username}")
            self.assertNotContains(blog_page, self.member.email)
            self.assertNotContains(blog_page, 'action="' + reverse("main:toggle_blog_star", args=[self.post.pk]) + '"')
            if role == "anonymous":
                self.assertContains(blog_page, reverse("main:login"))
            if role == "anonymous":
                self.assertNotContains(project_page, 'action="' + reverse("main:toggle_star", args=[self.project.pk]) + '"')
                self.assertContains(project_page, reverse("main:login"))
            else:
                self.assertContains(project_page, f'data-star-template="{reverse("main:toggle_star", args=["00000000-0000-0000-0000-000000000000"])}"')
                self.assertContains(project_page, 'id="project-csrf-token"')

    def test_blog_json_star_counts_current_user_state_and_privacy(self):
        other_post = BlogPost.objects.create(title="Unstarred blog", content="Other content")
        self.post.starred_by.add(self.member, self.editor)
        list_url = reverse("main:get_blog_json")
        detail_url = reverse("main:show_blog_json_by_id", args=[self.post.pk])
        for role, client in self.clients.items():
            with self.subTest(role=role):
                with CaptureQueriesContext(connection) as queries:
                    response = client.get(list_url)
                self.assertEqual(response.status_code, 200)
                collection_queries = [
                    query["sql"] for query in queries.captured_queries
                    if BlogPost._meta.db_table.lower() in query["sql"].lower()
                ]
                self.assertEqual(len(collection_queries), 1)
                if role != "anonymous":
                    self.assertIn("EXISTS", collection_queries[0].upper())
                records = {item["pk"]: item["fields"] for item in response.json()}
                self.assertEqual(set(records), {self.post.pk, other_post.pk})
                self.assertEqual(records[self.post.pk]["star_count"], 2)
                self.assertIs(records[self.post.pk]["is_starred"], role in ("member", "editor"))
                self.assertEqual(records[other_post.pk]["star_count"], 0)
                self.assertIs(records[other_post.pk]["is_starred"], False)
                for url in (list_url, detail_url):
                    public_response = client.get(url)
                    self.assertEqual(public_response.status_code, 200)
                    for item in public_response.json():
                        self.assertNotIn("starred_by", item["fields"])
                        self.assertNotIn("starred_by_names", item["fields"])
                    for user in (self.member, self.editor, self.owner):
                        self.assertNotIn(user.username, public_response.content.decode())
                        if user.email:
                            self.assertNotIn(user.email, public_response.content.decode())

    def test_blog_detail_json_keeps_serializer_contract(self):
        self.post.starred_by.add(self.member)
        response = self.clients["member"].get(
            reverse("main:show_blog_json_by_id", args=[self.post.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(set(data[0]), {"model", "pk", "fields"})
        self.assertEqual(data[0]["model"], "main.blogpost")
        self.assertEqual(data[0]["pk"], self.post.pk)
        self.assertIs(type(data[0]["pk"]), int)
        self.assertEqual(set(data[0]["fields"]), {
            "title", "content", "category", "picture_link", "created_at",
        })
        self.assertEqual(data[0]["fields"]["title"], self.post.title)
        self.assertEqual(data[0]["fields"]["content"], self.post.content)

    def test_csrf_rejects_all_mutations_without_token(self):
        for user, url, payload in (
            (self.owner, reverse("main:create_project"), self.project_data),
            (self.editor, reverse("main:update_project", args=[self.project.pk]), self.project_data),
            (self.owner, reverse("main:delete_project", args=[self.project.pk]), {}),
            (self.member, reverse("main:toggle_star", args=[self.project.pk]), {}),
            (self.member, reverse("main:toggle_blog_star", args=[self.post.pk]), {}),
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
