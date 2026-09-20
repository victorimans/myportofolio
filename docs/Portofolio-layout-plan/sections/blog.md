# Blog Section

**Status:** Specification updated; implementation completion pending

**Parent plan:** [Portfolio layout plan](../portfolio-layout-plan.md)

## Purpose

Add a dedicated Blog page that presents Victoriano's personal and technical writing. Blog is a dynamic exception to the otherwise static landing-page content: each database object represents one blog post.

The Blog page is separate from Projects and Journey. Projects remains the area for software and technology work, while Journey remains the area for academic, competition, mentorship, and professional milestones.

## Naming

- User-facing section: `Blog`
- Canonical content type: `Blog post`
- Django model: `BlogPost`
- List view: `show_blog`
- Create view: `create_blog`
- Update view: `update_blog`
- Delete view: `delete_blog`
- JSON view: `get_blog_json`
- Named list route: `main:show_blog`
- Named create route: `main:create_blog`
- Named update route: `main:update_blog`
- Named delete route: `main:delete_blog`
- Named JSON route: `main:get_blog_json`
- List URL: `/blog/`
- Create URL: `/blog/add/`
- Update URL: `/blog/<int:id>/edit/`
- Delete URL: `/blog/<int:id>/delete/`
- JSON URL: `/api/blog/`
- List template: `templates/blog.html`
- Form template: `templates/blog_form.html`
- Context variable for the list: `blog_posts`

`BlogPost` is preferred over `Blog` because each record represents one written post, not the whole blog. `Article` is also understandable, but `BlogPost` matches the user-facing Blog section most directly.

## Shared HTML template contract

- `templates/base.html` is the root HTML template for the portfolio pages.
- Every complete HTML page involved in the Blog feature must extend `base.html` with `{% extends "base.html" %}`.
- `base.html` owns the document declaration, `<html>`, `<head>`, shared assets, navbar, message area, footer, and shared scripts.
- `blog.html` and `blog_form.html` must provide page-specific blocks only; they must not duplicate the root document structure, navbar, footer, or shared asset links.
- Existing page templates such as `index.html` and `experience.html` must follow the same inheritance pattern.
- The Blog feature must not introduce a second root HTML template or duplicate shared markup.

## Content contract

The page should use the existing English interface style:

- Page/section label: `Blog`
- Each post displays its title, full content, creation date, and category.
- The date uses a simple format such as `12 September 2026`.
- Plain-text line breaks are preserved with Django's `linebreaks` filter.
- Django autoescape remains enabled; database content must not be treated as raw HTML.
- When `picture_link` is present, the post may display it as an image using the existing responsive styling; when it is empty, the post remains complete without an image.
- Empty state: `No blog posts have been added yet.`

Do not add fabricated posts, seed data, or fixture data. The page should be empty until a post is added through the public Blog form or Django Admin.

## Data model contract

`BlogPost` has Django's automatic `BigAutoField` primary key and the following additional fields:

| Field | Type | Required | Editable through `BlogPostForm` | Purpose |
| --- | --- | --- | --- | --- |
| `title` | `CharField(max_length=255)` | Yes | Yes | Post title |
| `content` | `TextField` | Yes | Yes | Full plain-text post content |
| `category` | `CharField(max_length=30, choices=BLOG_CATEGORY_CHOICES, default="ai")` | Yes | Yes | Post classification |
| `picture_link` | `URLField(blank=True, null=True)` | No | Yes | Optional image URL |
| `created_at` | `DateTimeField(auto_now_add=True)` | Automatic | No | Creation timestamp and display/order date |

The category choices are:

- `ai` — `AI`
- `dsa` — `DSA`
- `web-development` — `Web Development`
- `career` — `Career`
- `personal` — `Personal`

Posts are ordered newest first with `created_at` descending and `id` descending as the deterministic tie-breaker.

The model, migration, and database schema must agree. Because the current BlogPost migration predates `category` and `picture_link`, a new migration must be created and applied for those fields before the expanded workflow is considered complete.

## Page and navigation contract

- Register `path("blog/", show_blog, name="show_blog")` in `main/urls.py`.
- The list view obtains BlogPost data through the JSON serialization flow described below and passes deserialized objects as `blog_posts` to `blog.html`.
- The template loops over every object using Django Template Language.
- The template uses `{% empty %}` or an equivalent empty branch for the no-posts state.
- The Blog navbar link uses `{% url 'main:show_blog' %}`.
- The link appears after `Experience` and before `Contact` in the shared navbar owned by `base.html`.
- Keep the existing navbar, footer, Bootstrap setup, and responsive visual identity consistent with the other pages.
- Reuse existing responsive layout styles and add only the minimum Blog-specific CSS needed.

## Form contract

`BlogPostForm` is a `ModelForm` defined in `main/forms.py` for `BlogPost`.

- The form includes the editable fields `title`, `content`, `category`, and `picture_link`.
- The form excludes the automatic `id` and `created_at` fields.
- The form therefore represents at least three data fields with varied types: character data, text data, choice data, and an optional URL.
- All included fields must be rendered and fillable by the user; optionality applies only to `picture_link` as defined by the model.
- The form uses `POST` and `{% csrf_token %}`.
- Field-level validation errors are rendered next to the corresponding fields.
- The same `blog_form.html` template is reused for create and update workflows.
- The form action, heading, and submit label must identify whether the user is creating or updating a post.

### Create workflow

- The create form is available at `/blog/add/` through `main:create_blog`.
- A `GET` request renders an empty `BlogPostForm`.
- A valid `POST` saves one `BlogPost`, shows a success message, and redirects to `/blog/`.
- An invalid `POST` redisplays the submitted values and field-level validation errors.

### Update workflow

- The update form is available at `/blog/<int:id>/edit/` through `main:update_blog`.
- The view retrieves the selected BlogPost and binds it to `BlogPostForm(instance=blog_post)`.
- A `GET` request renders the existing values.
- A valid `POST` saves the edited values, shows a success message, and redirects to `/blog/`.
- An invalid `POST` redisplays the submitted values and field-level validation errors.
- The update form must not replace or modify `created_at`.

## Delete contract

- Delete is available at `/blog/<int:id>/delete/` through `main:delete_blog`.
- The delete view accepts `POST` only and retrieves the selected BlogPost by primary key.
- The view deletes the record, shows a success message, and redirects to `/blog/`.
- Each rendered post provides a visible Delete button connected to this route.
- The delete control is a form submission with `{% csrf_token %}`, not a destructive `GET` link.
- A missing BlogPost returns the normal Django 404 response.

## JSON and deserialization contract

- Register `path("api/blog/", get_blog_json, name="get_blog_json")` in `main/urls.py`.
- `get_blog_json` accepts `GET` and serializes all BlogPost records as JSON with `content_type="application/json"`.
- JSON results use the agreed newest-first ordering: `-created_at`, then `-id`.
- `show_blog` obtains the JSON response from `get_blog_json`, decodes its content, and deserializes it with Django's JSON deserializer.
- `show_blog` passes the resulting BlogPost objects to `blog.html` for normal HTML rendering.
- The JSON flow must preserve `title`, `content`, `category`, `picture_link`, and `created_at` values.
- A per-ID JSON view is not required for the public acceptance criteria unless it is separately routed and tested.

## Admin contract

Register `BlogPost` with the default Django Admin. The Admin remains an alternative editing workflow for the complete model; no custom `ModelAdmin`, search, filters, or preview is needed.

## Required migration and tests

The implementation must create and apply a migration that adds `category` and `picture_link` to the existing BlogPost table. The migration file must be included with the implementation.

At minimum, add tests for:

1. `/blog/` is accessible and uses `blog.html`.
2. Blog templates extend `base.html` and do not duplicate the root document structure.
3. A stored BlogPost's title, content, category, optional image, and formatted creation date appear correctly in the HTML.
4. The empty state appears when no BlogPost exists.
5. `/blog/add/` renders all editable form fields and a valid submission creates a BlogPost.
6. `/blog/<int:id>/edit/` renders existing values and a valid submission updates the BlogPost.
7. The delete button submits a CSRF-protected `POST` request and removes the BlogPost.
8. `/api/blog/` returns JSON with the expected BlogPost fields and ordering.
9. `/blog/` displays objects after obtaining and deserializing the JSON response.
10. Newest-first ordering and deterministic same-timestamp ordering remain protected.
11. Plain-text line breaks are preserved and HTML content is escaped.
12. `python manage.py runserver` starts without errors.

## Implementation checklist

### Existing implementation to preserve

- [x] Define `BlogPost` in `main/models.py`.
- [x] Define `BlogPostForm` in `main/forms.py` with the four editable fields.
- [x] Implement `create_blog` and the `/blog/add/` route.
- [x] Implement `show_blog` with JSON serialization and deserialization.
- [x] Render `blog.html` and `blog_form.html` through `base.html`.
- [x] Register the Blog link in the shared navbar.
- [x] Render the title, content, creation date, and empty state.

### Required completion work

- [ ] Create and apply a migration for `category` and `picture_link`.
- [ ] Register `update_blog` in `main/urls.py` at `/blog/<int:id>/edit/`.
- [ ] Register `delete_blog` in `main/urls.py` at `/blog/<int:id>/delete/`.
- [ ] Register `get_blog_json` in `main/urls.py` at `/api/blog/`.
- [ ] Make `blog_form.html` use a dynamic create/update action, heading, and submit label.
- [ ] Add update controls for each rendered BlogPost.
- [ ] Add CSRF-protected delete buttons for each rendered BlogPost.
- [ ] Render category and the optional picture link/image on the Blog page.
- [ ] Keep the automatic `id` and `created_at` fields out of the form.
- [ ] Add tests for create, update, delete, JSON, deserialization, field rendering, template inheritance, and schema consistency.
- [ ] Run `python manage.py check` successfully.
- [ ] Run `python manage.py test` successfully.
- [ ] Run `python manage.py runserver` and confirm startup without errors.
- [ ] Verify that an Admin-created post appears on `/blog/`.
- [ ] Verify that a post created through `/blog/add/` appears on `/blog/`.
- [ ] Verify that a post updated through `/blog/<int:id>/edit/` shows its new values.
- [ ] Verify that a post deleted through its button no longer appears on `/blog/`.

## Acceptance scenarios

### Empty database

When no BlogPost exists, `/blog/` returns HTTP 200, uses `blog.html`, renders no post card, and shows `No blog posts have been added yet.`

### Create a post

When a user submits valid title, content, category, and optional picture-link values through `/blog/add/`, one BlogPost is saved and the user is redirected to `/blog/`, where the new post is visible.

### Update a post

When a user opens `/blog/<int:id>/edit/`, the form contains the selected post's current values. Submitting valid changed values updates that same record and the changed post is visible on `/blog/`.

### Delete a post

When a user submits the CSRF-protected Delete button for a post, that BlogPost is removed and the user is redirected to `/blog/` without the deleted post.

### One or more posts

When posts exist, every post appears with its title, full content, category, formatted creation date, and optional image when supplied. Newer posts appear first.

### Same creation timestamp

When posts share the same `created_at`, the larger automatic `id` appears first.

### JSON-backed listing

When `/blog/` is requested, the view obtains the BlogPost collection in JSON form, deserializes it into BlogPost objects, and renders those objects in the HTML response.

### Plain-text content

Content containing line breaks remains readable as separate lines or paragraphs. HTML entered as content is escaped rather than executed.

### Admin workflow

A user can create or edit a complete BlogPost through the default Django Admin, and the saved record appears on `/blog/`.

### Shared template inheritance

The rendered Blog list and form pages inherit the shared document structure, navbar, footer, and assets from `base.html` without duplicating those elements in the page templates.

## Explicitly out of scope

- Individual post detail pages or slug-based URLs
- Pagination or infinite scrolling
- Draft/published status
- Author fields
- Excerpts
- Markdown or rich-text editing
- Raw HTML rendering
- Seed data or fixtures
- New dependencies
- A second root HTML template
- Duplicated navbar, footer, or document markup in Blog templates
- Per-ID JSON routes unless separately requested

## Verification log

The previous verification log covered only the earlier create/list Blog scope and is not sufficient for this expanded specification. In particular, it did not verify the new update, delete, public JSON route, complete form workflow, template controls, or the migration for `category` and `picture_link`.

Current repository facts requiring verification after implementation:

- [x] The Blog model and form currently declare `category` and `picture_link`.
- [x] `show_blog` currently performs JSON serialization and deserialization before rendering.
- [x] `blog.html` and `blog_form.html` currently extend `base.html`.
- [ ] The database migration state matches the current BlogPost model.
- [ ] Update, delete, and JSON routes are registered and reachable.
- [ ] The form action and controls support both create and update.
- [ ] Each post has a working CSRF-protected delete button.
- [ ] Category and optional image data are rendered correctly.
- [ ] Expanded automated tests pass.
- [ ] `python manage.py runserver` starts without errors after the expanded implementation.
- [ ] Live desktop/mobile behavior remains unverified unless a browser target is available.
