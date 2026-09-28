# Blog Section

**Status:** Core Blog implementation and runtime verification complete; role-based authorization specification agreed; authorization implementation pending; live visual verification pending

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

Do not add fabricated posts, seed data, or fixture data. The page should be empty until a post is added by an authorized superuser through the Blog form or by a Django Admin user with the relevant Admin permission.

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
- Each rendered post provides a Delete button only to a superuser, connected to this route.
- The delete control is a form submission with `{% csrf_token %}`, not a destructive `GET` link.
- A missing BlogPost returns the normal Django 404 response.

## Authorization, Editor role, and public Blog content

This section is the agreed access-control specification for the existing Blog workflow. It augments the earlier functional contracts above. BlogPost has no star feature in this scope. The four roles have the same capabilities as the Projects policy, but the data resource is BlogPost and Django Admin remains a separate permission-governed workflow.

### Current authorization baseline

Checked against the repository on 2026-09-28. Treat these as observations, not implemented requirements:

- `create_blog` and `update_blog` require login and then currently allow only `is_superuser`; both accept GET and POST.
- `delete_blog` requires login, accepts POST, and currently allows only `is_superuser`.
- `blog.html` currently shows the create control to superusers but renders edit and delete controls for every visitor.
- The current workspace also contains an uncommitted `BlogPost.starred_by` field, a star migration, `toggle_blog_star`, and Blog star controls/tests. These are present in the current working tree but conflict with the agreed Blog domain, which has no star interaction. The agreed target removes the Blog star feature, endpoint, controls, field, and relation.
- Because the user confirmed that Blog star memberships may be deleted together with the relation, a future implementation may use an explicit schema migration that removes `BlogPost.starred_by` and its join table/data. The migration must be reviewed and applied deliberately; do not silently delete unrelated Project stars or user accounts. No data export is required by the agreed product contract.
- `show_blog` and `/api/blog/` are public. `/api/blog/<int:id>/` also exists and is public; the earlier functional acceptance only requires the collection endpoint. This authorization specification does not require a new detail page or route and any existing public JSON detail route remains read-only/public.
- Existing tests cover public access and CRUD, but their expectations must be checked against the new role matrix. Update authorization tests and template visibility assertions are required as part of a future implementation.
- The login view currently redirects to the landing page after authentication and does not appear to honor `next`; the agreed protected-flow contract requires safe continuation after login.

### Role and capability matrix

All BlogPost content is public: there is no draft/published state, and every existing BlogPost appears in public list and JSON reads. Authentication is required only for mutation actions.

| Capability | Anonymous visitor | Authenticated user | Editor | Superuser (Project owner) |
|---|---:|---:|---:|---:|
| Read Blog list HTML | Allow | Allow | Allow | Allow |
| Read Blog collection JSON | Allow | Allow | Allow | Allow |
| Read existing Blog detail JSON | Allow | Allow | Allow | Allow |
| Create BlogPost | Login redirect | 403 | 403 | Allow |
| Update BlogPost content | Login redirect | 403 | Allow | Allow |
| Delete BlogPost | Login redirect | 403 | 403 | Allow |
| Star/unstar BlogPost | Not available | Not available | Not available | Not available |

The Editor role is membership in the exact Django Group named `Editor`, assigned and revoked through Django Admin. Membership permits updating BlogPost content only; it does not permit creation or deletion and does not imply Django Admin permissions. Superuser status permits Blog form create/update/delete regardless of Editor Group membership.

### Server-side checks and HTTP behavior

1. Enforce the capability matrix in every public Blog mutation view. Hiding a control in `blog.html` is only presentation and never an authorization check.
2. Create and update use GET to display a form and POST to validate/save. An authorized superuser GET to create and an authorized Editor/superuser GET to update return 200 without mutating data.
3. Delete is POST-only. GET or any unsupported method must not delete a post.
4. Anonymous requests to protected Blog mutation endpoints redirect to the configured login URL and preserve a safe `next` destination, including requests made with unsupported methods. After login, return to that safe local destination; reject external/unsafe destinations and use the normal post-login destination instead.
5. For authenticated users, authorization denial takes precedence over method acceptance: a user who lacks the capability receives 403 for GET or POST to a protected operation. For a permitted user, unsupported methods receive 405. No unsupported request mutates data.
6. POST create, update, and delete forms include `{% csrf_token %}` and rely on Django CSRF middleware. A rejected CSRF request must leave the database unchanged.
7. Resolve update/delete targets by the URL's integer primary key; return 404 for missing BlogPost records without changing other records.
8. Invalid create/update data redisplays the form with field errors and submitted values; it must not create or partially update a record.
9. A valid create/update/delete displays the existing success message and redirects to `/blog/` (Post/Redirect/Get). Delete must not be available as a state-changing GET.
10. The Blog form writable fields remain `title`, `content`, `category`, and `picture_link`. `id` and `created_at` remain server-managed; crafted POST values for them must not change them. `created_at` remains immutable during update.

### Editor and Django Admin boundary

- The `Editor` Group is an application role for the public Blog and Projects views. Adding or removing membership must affect the next authorization check.
- Do not auto-assign Editor during registration.
- Django Admin is a separate trusted management surface. Its actions are governed by Django's model-level Admin permissions and staff/superuser configuration, not by the public-view role matrix. An Editor Group member does not gain Admin access merely by being an Editor.
- Admin workflows must continue to work for accounts that have appropriate Django Admin permissions. The Blog authorization implementation must not grant public-view capabilities by weakening Admin authentication or permissions.
- The existing default BlogPost Admin registration may remain. Any question of granting a particular Editor account Django Admin model permissions is an administrator decision independent of Editor Group membership.

### Blog template and navigation controls

- Keep the Blog list, content, ordering, category, image, empty state, and public navigation available to every visitor.
- Show `Tambah Blog` only to a superuser.
- Show `Edit Blog` only to Editor members and superusers.
- Show `Hapus Blog` only to superusers, as a CSRF-protected POST form.
- Show no star/unstar controls or star count for BlogPost.
- The target Blog model has no `starred_by` relation or Blog-specific star join table. Remove/retire the Blog star route and implementation; Projects star data and routes are unaffected.
- Keep the view-level authorization checks even when controls are hidden; crafted direct requests must receive the matrix's HTTP result.
- Preserve semantic buttons/links, labels, keyboard accessibility, and existing template inheritance from `base.html`.

### JSON and content privacy contract

- `/api/blog/` remains a public GET collection endpoint and preserves the agreed BlogPost fields, ordering (`-created_at`, then `-id`), and `application/json` content type.
- The existing per-ID JSON route, if retained, remains a public GET-only read route returning one BlogPost or 404.
- Neither route may expose account credentials, session data, role membership, or unrelated private user data. Current BlogPost has no User relationship; do not add one for authorization.
- JSON routes do not provide create, update, delete, star, or role-management operations.
- Keep the existing JSON-backed list rendering flow unless a later approved specification changes it.

### Blog authorization acceptance matrix

Test each role with separate clients and test both rendered controls and direct server requests. Use a CSRF-enforcing test client for CSRF rejection cases.

| Scenario | Expected result |
|---|---|
| Anonymous/user/Editor/superuser GET `/blog/` | 200; same public post collection and content visibility |
| Anonymous/user/Editor/superuser GET `/api/blog/` | 200; same public ordered JSON content |
| Anonymous GET existing per-ID JSON route | 200 for existing post; 404 for unknown ID |
| Anonymous GET or POST create/update/delete | Redirect to login with safe `next`; no data change |
| Anonymous protected request after login | Return to safe local `next`; external/unsafe destination falls back to normal destination |
| Ordinary authenticated user GET or POST create | 403; no post created |
| Ordinary authenticated user GET or POST update | 403; post unchanged |
| Ordinary authenticated user GET or POST delete | 403; post remains |
| Editor GET or POST create | 403; no post created |
| Editor GET update | 200; existing values shown; no mutation |
| Editor POST valid update | Success; allowed content fields changed; creation timestamp unchanged |
| Editor GET or POST delete | 403; post remains |
| Superuser GET create/update | 200; correct form rendered; no mutation |
| Superuser POST valid create/update | Success; only allowed fields persisted; redirect to `/blog/` |
| Superuser POST valid delete | Success; target post removed; redirect to `/blog/` |
| Permitted create/update POST with invalid fields | Validation errors and submitted values shown; no mutation |
| Authenticated permitted caller uses unsupported method on create/update/delete | 405; no mutation |
| Authenticated unauthorized caller uses GET or POST on protected view | 403; no mutation |
| Missing BlogPost ID for update/delete | 404; no mutation |
| Create/update/delete POST without valid CSRF token | Rejected; no database change |
| Submitted `created_at` or `id` in crafted form payload | Values are ignored; server-managed values remain unchanged |
| Editor membership added then update attempted | Update allowed on subsequent request |
| Editor membership removed then update attempted | 403; post unchanged |
| New registered user without Editor membership | Ordinary-user capabilities only |
| Superuser with/without Editor membership | Same superuser capabilities |
| Blog list for anonymous user | No create/edit/delete/star controls; all post content remains readable |
| Blog list for ordinary user | No create/edit/delete/star controls; all post content remains readable |
| Blog list for Editor | Edit controls only; no create/delete/star controls |
| Blog list for superuser | Create/edit/delete controls; no star controls |
| Any Blog list/JSON response | No star count, star relation, or private account information |
| Blog schema after target migration | No BlogPost star relation or Blog star join table; Project star relation remains intact |
| Existing Blog star memberships during migration | Deleted as explicitly approved; no Project stars or User accounts are deleted |
| Django Admin Blog CRUD by account with relevant Admin permissions | Continues to follow Django Admin permissions independently of public-view role |

### Completion criteria for a future implementation

- [x] Public reads remain anonymous and preserve all Blog content, ordering, empty-state, and JSON behavior.
- [x] Server-side create/update/delete authorization matches the four-role matrix.
- [x] `Editor` membership is manageable in Django Admin, grants update only in public Blog views, and is not assigned automatically at registration.
- [x] Create/update GET and POST behavior, delete POST-only behavior, 403/405 precedence, `next` redirect, safe local redirect validation, and 404 behavior match this contract.
- [x] CSRF is validated for every mutation form; invalid input or rejected requests do not mutate records.
- [x] Templates expose controls to the correct roles and no Blog star controls are presented.
- [x] Blog star route, view, relation, and join table are removed through a reviewed migration; Project star behavior/data remain unchanged.
- [x] Django Admin remains separately permission-protected and operational for authorized staff.
- [x] JSON collection and existing detail reads remain public and contain only public BlogPost data.
- [x] Relevant tests cover the full acceptance matrix, including direct unauthorized requests and CSRF-enforcing client behavior.
- [x] Existing Blog functional checks remain valid; schema/migrations remain consistent; `python manage.py check` and `python manage.py runserver` succeed.

### Explicit non-goals for Blog authorization

- BlogPost stars, likes, reactions, or per-user interaction state; any existing Blog star memberships may be deleted with the relation as approved.
- Draft/published visibility, author ownership, or per-post access rules.
- Applying the public-view Editor restrictions to Django Admin's separate permission model.
- Adding a new detail page or API route; existing list and JSON routes remain public as described above.
- Changing Blog fields, category vocabulary, display copy, ordering, content-rendering rules, or root template architecture as part of authorization work.

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
- [x] Implement `create_blog` and the `/blog/add/` route. The route exists; access is subject to the role-based authorization specification above.
- [x] Implement `show_blog` with JSON serialization and deserialization.
- [x] Render `blog.html` and `blog_form.html` through `base.html`.
- [x] Register the Blog link in the shared navbar.
- [x] Render the title, content, creation date, and empty state.

### Required completion work

- [x] Create and apply a migration for `category` and `picture_link`.
- [x] Register `update_blog` in `main/urls.py` at `/blog/<int:id>/edit/`.
- [x] Register `delete_blog` in `main/urls.py` at `/blog/<int:id>/delete/`.
- [x] Register `get_blog_json` in `main/urls.py` at `/api/blog/`.
- [x] Make `blog_form.html` use a dynamic create/update action, heading, and submit label.
- [x] Add update controls for each rendered BlogPost.
- [x] Add CSRF-protected delete buttons for each rendered BlogPost.
- [x] Render category and the optional picture link/image on the Blog page.
- [x] Keep the automatic `id` and `created_at` fields out of the form.
- [x] Add tests for create, update, delete, JSON, deserialization, field rendering, template inheritance, and schema consistency.
- [x] Run `python manage.py check` successfully.
- [x] Run `python manage.py test` successfully.
- [x] Run `python manage.py runserver` and confirm startup without errors.
- [x] Verify that an Admin-created post appears on `/blog/`.
- [x] Verify that a post created through `/blog/add/` appears on `/blog/`.
- [x] Verify that a post updated through `/blog/<int:id>/edit/` shows its new values.
- [x] Verify that a post deleted through its button no longer appears on `/blog/`.

## Acceptance scenarios

### Empty database

When no BlogPost exists, `/blog/` returns HTTP 200, uses `blog.html`, renders no post card, and shows `No blog posts have been added yet.` Every BlogPost that does exist is publicly readable; the role policy gates mutations only.

### Create a post

When a superuser submits valid title, content, category, and optional picture-link values through `/blog/add/`, one BlogPost is saved and the user is redirected to `/blog/`, where the new post is visible. An ordinary user or Editor cannot create through a direct request.

### Update a post

When an Editor or superuser opens `/blog/<int:id>/edit/`, the form contains the selected post's current values. Submitting valid changed values updates that same record and the changed post is visible on `/blog/`. An ordinary user receives HTTP 403.

### Delete a post

When a superuser submits the CSRF-protected Delete button for a post, that BlogPost is removed and the user is redirected to `/blog/` without the deleted post. An ordinary user or Editor receives HTTP 403 and the post remains.

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

Runtime verification on 2026-09-20:

- [x] The Blog model and form declare `category` and `picture_link`.
- [x] Migration `0004_blogpost_category_picture_link` was applied successfully.
- [x] `show_blog` performs JSON serialization and deserialization before rendering.
- [x] `blog.html` and `blog_form.html` extend `base.html`.
- [x] Update, delete, and JSON routes are registered and reachable.
- [x] The form action, heading, and submit label support both create and update.
- [x] Each post has a working CSRF-protected delete button.
- [x] Category and optional image data are rendered correctly.
- [x] The expanded test suite passed with 30 tests.
- [x] `python manage.py check` passed with no issues.
- [x] `python manage.py makemigrations --check --dry-run` reported no changes.
- [x] `python manage.py runserver` started successfully and `/blog/` returned HTTP 200.
- [x] Admin, create, update, and delete workflows are covered by automated tests.
- [x] Role-based Blog authorization and control visibility passed automated checks on 2026-09-28 (43 tests); migration and Django checks passed, and `/blog/` returned HTTP 200.
- [ ] Live desktop/mobile behavior remains unverified because the browser integration was unavailable.
