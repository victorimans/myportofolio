import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import BlogPost, Project


class BlogPostAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="blog-owner", password="test-password", email="owner@example.com",
        )
        self.member = User.objects.create_user(username="blog-member", password="test-password")
        self.editor = User.objects.create_user(username="blog-editor", password="test-password")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.post = BlogPost.objects.create(
            title="Existing blog", content="Existing content", category="ai",
        )
        self.list_url = reverse("api:blogpost-list")
        self.detail_url = reverse("api:blogpost-detail", args=[self.post.pk])
        self.star_url = reverse("api:blogpost-star", args=[self.post.pk])
        self.payload = {
            "title": "New blog", "content": "A useful post", "category": "career",
            "picture_link": "https://example.com/blog.png",
        }

    def test_public_list_and_detail_and_title_search(self):
        response = self.client.get(self.list_url, {"title": "EXIST"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.post.pk)
        self.assertNotIn("starred_by", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(self.list_url, {"title": "missing"}).data, [])

    def test_owner_can_create_and_validation_errors_are_returned(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(BlogPost.objects.filter(pk=response.data["id"]).exists())
        persisted_posts = list(BlogPost.objects.values_list("pk", "title", "content", "category"))
        for changes in ({"title": "  "}, {"content": "<b></b>"}, {"category": "unknown"}):
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                list(BlogPost.objects.values_list("pk", "title", "content", "category")),
                persisted_posts,
            )

    def test_guest_and_regular_user_cannot_write_and_database_stays_unchanged(self):
        original_posts = list(BlogPost.objects.values_list("pk", "title", "content", "category"))
        for user in (None, self.member):
            with self.subTest(user=user):
                self.client.force_authenticate(user=user)
                responses = (
                    self.client.post(self.list_url, self.payload, format="json"),
                    self.client.patch(self.detail_url, {"title": "Denied"}, format="json"),
                    self.client.put(self.detail_url, self.payload, format="json"),
                    self.client.delete(self.detail_url),
                )
                self.assertEqual([response.status_code for response in responses], [403, 403, 403, 403])
                self.assertEqual(
                    list(BlogPost.objects.values_list("pk", "title", "content", "category")),
                    original_posts,
                )

    def test_editor_can_patch_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"title": "Edited title"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Edited title")
        self.assertEqual(self.post.content, "Existing content")

        original_posts = list(BlogPost.objects.values_list("pk", "title", "content", "category"))
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(
            list(BlogPost.objects.values_list("pk", "title", "content", "category")),
            original_posts,
        )

    def test_owner_can_create_and_delete_blog_posts(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_id = response.data["id"]
        self.assertTrue(BlogPost.objects.filter(pk=created_id, title="New blog").exists())

        response = self.client.delete(reverse("api:blogpost-detail", args=[created_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(BlogPost.objects.filter(pk=created_id).exists())

    def test_owner_can_update_and_delete_while_other_users_are_forbidden(self):
        self.client.force_authenticate(user=self.member)
        self.assertEqual(self.client.patch(self.detail_url, {"title": "Denied"}, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 200)
        self.assertEqual(self.client.delete(self.detail_url).status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(BlogPost.objects.filter(pk=self.post.pk).exists())

    def test_authenticated_user_can_toggle_star(self):
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.client.force_authenticate(user=self.member)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_browser_session_writes_require_and_accept_csrf_header(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="blog-owner", password="test-password"))
        token_response = client.get(reverse("main:show_blog"))
        self.assertEqual(token_response.status_code, 200)
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post(self.list_url, self.payload, format="json").status_code, 403)
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.project = Project.objects.create(
            title="Portfolio", description="My website", tech_stack="Django",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "New project", "description": "A useful app", "tech_stack": "Python",
            "project_url": "https://example.com/", "project_image_url": "",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, "My website")
        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_editor_can_update_but_cannot_create_or_delete_projects(self):
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Edited"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(self.detail_url).data["title"], "Edited")
        self.assertEqual(self.client.get(self.detail_url).data["description"], "My website")
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(self.detail_url).data["title"], "New project")
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(len(self.client.get(self.list_url).data), 1)
        self.assertEqual(self.client.get(self.detail_url).status_code, 200)

    def test_safe_methods_are_public_and_do_not_change_projects(self):
        editor = User.objects.create_user(username="editor")
        editor.groups.add(Group.objects.create(name="Editor"))
        for user in (None, self.visitor, editor, self.owner):
            self.client.force_authenticate(user=user)
            before = self.client.get(self.detail_url).data
            for url in (self.list_url, self.detail_url):
                for method in (self.client.get, self.client.head, self.client.options):
                    with self.subTest(user=user, url=url, method=method.__name__):
                        self.assertEqual(method(url).status_code, status.HTTP_200_OK)
            self.assertEqual(self.client.get(self.detail_url).data, before)
            self.assertEqual(len(self.client.get(self.list_url).data), 1)

    def test_staff_or_differently_named_group_cannot_update(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name="editor"))
        self.client.force_authenticate(user=self.visitor)
        for method in (self.client.put, self.client.patch):
            self.assertEqual(method(self.detail_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.get(self.detail_url).data["title"], "Portfolio")

    def test_editor_can_toggle_own_star(self):
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_starred"])

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        # The Browsable API form renders a real CSRF token into the response.
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)