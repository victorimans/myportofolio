# Blog: Assignment 5 Interactivity Specification

Status: AJAX listing and case-insensitive partial-title search with 300 ms debounce are implemented. Superuser modal creation with CSRF-protected AJAX POST, JSON validation/authorization responses, shared toast feedback, and query-preserving list refresh is implemented. Server-side Blog form tag stripping and live browser verification remain outstanding. Source and this status were reconciled on 2026-10-04. The checklist distinguishes implemented behavior from outstanding work and browser verification.

Parent plan: [Portfolio layout and implementation](../portfolio-layout-plan.md)

## Purpose and domain boundaries

Blog is a public, database-backed area for Victoriano's personal and technical writing. It is separate from static landing-page content, database-backed Projects, and the Experience listing. Blog posts are readable without authentication. Assignment 5 applies the Tutorial 05 AJAX interaction pattern to Blog while preserving the roles established for Assignment 4.

The term **Blog post** means one published public writing record. The current domain has no draft visibility or separate publish state. A post has a title, body, category, optional picture link, creation date, and star memberships.

## Existing data contract

`BlogPost` currently has an automatic integer primary key and these fields:

| Field | Type | Form writable | Purpose |
| --- | --- | --- | --- |
| `title` | `CharField(max_length=255)` | Yes | Post title; Assignment 5 search target. |
| `content` | `TextField` | Yes | Plain-text body, displayed with line breaks. |
| `category` | `CharField(max_length=30)` | Yes | One of AI, DSA, Web Development, Career, Personal; default `ai`. |
| `picture_link` | Optional URL field | Yes | Optional post image. |
| `created_at` | Automatic creation timestamp | No | Visible creation date and ordering. |
| `starred_by` | Many-to-many to Django `User` | No | Per-user star membership; not writable in the form. |

Posts are ordered newest first by `-created_at`, then `-id`. Preserve that deterministic ordering in both HTML list presentation and JSON responses.

## Routes and current behavior

| URL | Name | Current behavior | Assignment 5 target |
| --- | --- | --- | --- |
| `/blog/` | `main:show_blog` | Public shell-only HTML page with title search; Fetch loads cards without navigation and debounces typing for 300 ms. | Render the page shell and controls, then load cards from the public JSON collection using Fetch. |
| `/blog/add/` | `main:create_blog` | Legacy superuser GET/POST traditional create form at `templates/blog_form.html`; the listing now uses a modal. | Retained for compatibility. |
| `/blog/add-ajax/` | `main:create_blog_ajax` | Superuser-only POST validated with `BlogPostForm`; returns JSON `201`, `400`, or `403` and requires CSRF. | Used by the create modal on `/blog/`. |
| `/blog/<int:id>/edit/` | `main:update_blog` | Editor/superuser GET/POST update form. | Preserve this existing Assignment 4 behavior unless separately changed by an explicit decision. |
| `/blog/<int:id>/delete/` | `main:delete_blog` | Superuser POST-only delete. | Preserve role restriction and POST/CSRF protection. |
| `/blog/<int:blog_id>/star/` | `main:toggle_blog_star` | Authenticated POST-only star toggle. | Preserve role restriction and ensure the AJAX JSON provides the count and current caller's own state. |
| `/api/blog/` | `main:get_blog_json` | Public GET collection manually composed with JsonResponse; accepts a trimmed, case-insensitive partial `title` query and includes aggregate star count and caller-specific star state. | Return manually constructed JSON with optional title query and star information. |
| `/api/blog/<int:id>/` | `main:show_blog_json_by_id` | Public GET serialized detail or 404. | No change required for Assignment 5 unless the implementation chooses to share collection serialization logic. |

All complete pages extend `templates/base.html`, which provides shared assets, toast support through `static/js/toast.js`, navbar, messages, footer, and scripts. The Blog page should load any new page behavior from a dedicated static JavaScript file; do not embed untrusted post content into inline HTML.

## Assignment 5 target behavior

### 1. AJAX list and manually composed JSON

- Keep `/blog/` public. Render the page frame, search control, states, and empty results container without server-rendering the post list.
- Fetch the public collection from `/api/blog/`; the endpoint must be usable by anonymous users as well as all authenticated roles.
- Construct response objects manually with `JsonResponse`, rather than returning Django's model serializer output. Include only the needed public fields, such as `id`, `title`, `content`, `category`, a display category if useful, `picture_link`, `created_at`, `star_count`, and `is_starred`.
- `star_count` is the number of distinct users who starred that post. `is_starred` is true only when the requesting authenticated user starred that post; use false for anonymous visitors.
- Never include usernames, account identifiers, or a list of star members. Public API data must not identify individual users.
- Preserve newest-first order (`-created_at`, `-id`). If the page formats date strings in JavaScript, specify and handle a stable date representation from the API.
- Render a visible loading state while the request is pending, an empty state when no posts match, and an error state with retry when the request fails. Handle non-2xx responses and JSON parsing/network errors.
- Avoid stale-response races if the user changes the search while a request is in progress; abort superseded requests or otherwise ignore stale results.

### 2. Title search with debouncing

- Provide search on Blog post title, matching partial strings case-insensitively.
- Send the search query to `/api/blog/` (for example, `?title=<query>`); do not reload the page.
- Debounce input so the request occurs only after the user stops typing for 300 ms, matching the implemented Projects interaction pattern. Submitting the search form may run immediately.
- Preserve the current query in the input and optionally synchronize it with the URL without navigation.
- Search is over public Blog posts only; there is no draft/private post visibility in the current domain.

### 3. Superuser create modal and AJAX POST

- Show an add-post control and modal only to a superuser. The view must independently enforce this rule; hiding the modal is not authorization.
- The modal form uses `BlogPostForm` and includes the CSRF token. Submit with Fetch to a dedicated POST endpoint (recommended: `/blog/add-ajax/`) using either the `csrfmiddlewaretoken` form field or the `X-CSRFToken` header.
- The endpoint validates through `BlogPostForm` and returns JSON with appropriate HTTP statuses: `201` for successful creation, `400` for invalid form data with field validation messages, and `403` for a caller without create permission.
- On success, close/reset the modal, show a success toast, and refresh the current list/search without a full-page navigation.
- On failure, retain usable form state and show an error toast. Include server field validation messages in the error feedback; do not silently discard them.
- Preserve Assignment 4 role policy: superuser creates and deletes; exact `Editor` group membership grants update only; any authenticated user may star/unstar; anonymous visitors may read.
- Preserve traditional `/blog/add/` only if it remains useful for compatibility; it is not the required primary create flow for Assignment 5.

### 4. Toast feedback

- Reuse `showToast` supplied by `static/js/toast.js` through `base.html`.
- Show success feedback after creation and error feedback for authorization, validation, network, or server failures.
- Validation feedback should communicate the messages returned by the server, including field-level errors when present.
- Do not add a second toast implementation if the shared helper already covers the behavior.

### 5. XSS protection

- Add `strip_tags` cleanup in `BlogPostForm.clean_title` and `BlogPostForm.clean_content`; reject a title that becomes empty after stripping. Normalize surrounding whitespace where appropriate.
- Treat every value received from JSON as untrusted. Construct nodes using DOM APIs and assign user-controlled text through `textContent`; do not build card markup by interpolating title/content/category into `innerHTML`.
- Preserve intended line breaks in plain-text content with safe text rendering (for example, text nodes with CSS `white-space: pre-line` or equivalent safe paragraph construction). Do not convert arbitrary post content into raw HTML.
- Use validated URL fields for picture links, and set image attributes as DOM properties. Do not use user-controlled strings in executable attributes or event handlers.
- Verify with a title/body payload such as `<img src="x" onerror="alert('XSS!')">`: tags should be removed by server-side form cleaning or rendered as harmless text, and no alert or script execution may occur.

## Authorization contract

| Capability | Anonymous | Authenticated regular user | Editor group | Superuser |
| --- | --- | --- | --- | --- |
| Read Blog HTML/JSON | Allow | Allow | Allow | Allow |
| Search public posts | Allow | Allow | Allow | Allow |
| Create BlogPost | Deny (403 on AJAX endpoint) | Deny (403) | Deny (403) | Allow |
| Update BlogPost content | Login redirect | 403 | Allow | Allow |
| Delete BlogPost | Login redirect | 403 | 403 | Allow |
| Star/unstar BlogPost | Login redirect | Allow | Allow | Allow |

`Editor` means membership in the exact Django Group named `Editor`; registration does not assign the group. Existing protected HTML mutation routes retain their established authentication/authorization behavior. The new create AJAX view must return JSON `403` for unauthorized callers rather than relying on template visibility. All state-changing requests remain POST-only and CSRF-protected.

## Existing security and rendering details to preserve

- `BlogPostForm` currently has fields `title`, `content`, `category`, and `picture_link`; primary key, timestamps, and star membership are not form-writable.
- Blog cards use text-safe DOM construction and preserve body line breaks without treating plain text as HTML. The search input uses Django template autoescape when restoring the query.
- Project's existing `ProjectForm` strips HTML and `static/js/projects.js` creates dynamic project card text with safe DOM APIs; Assignment 5 applies equivalent protections to Blog without changing Projects as part of this specification.
- JSON may show an aggregate star count and the requesting user's own `is_starred` value, but must not expose identity or membership of other users.

## Implementation checklist

- [x] Change `/blog/` to render the list shell and controls, not the post collection.
- [x] Add/update public GET collection JSON using manually composed `JsonResponse` data.
- [x] Include `star_count` and per-request `is_starred` while keeping star membership private.
- [x] Add case-insensitive, partial-title filtering to the JSON endpoint.
- [x] Add Blog page JavaScript with Fetch, request-race handling, and loading/error/retry/empty states.
- [x] Add 300 ms debounce for Blog title search.
- [x] Render title, category, date, content, image, star controls, and role-dependent edit/delete controls using text-safe DOM construction.
- [x] Add a superuser-only create modal on `/blog/` using `BlogPostForm`.
- [x] Add a POST AJAX create endpoint with `201`, `400`, and `403` JSON responses and server-side role enforcement.
- [x] Send CSRF token with the modal request.
- [x] Refresh the displayed list after successful creation without navigation.
- [x] Reuse shared toast helper for successful creation and authorization/validation/network errors.
- [ ] Strip tags in `clean_title` and `clean_content`; reject an empty-after-cleaning title.
- [x] Preserve exact Editor update-only and superuser create/delete permissions, plus authenticated star behavior.
- [x] Confirm all roles, including anonymous users, can load public Blog data.
- [x] Confirm all roles, including anonymous users, can search public Blog data.
- [x] Run `python manage.py check` and the Django test suite; do not report checks as passed without actually running them.
- [ ] Run the application with `python manage.py runserver` and manually verify list loading, search, modal create, toast feedback, stars, and permissions for anonymous, regular, Editor, and superuser sessions.
- [ ] Test an XSS payload such as `<img src="x" onerror="alert('XSS!')">`; verify no executable markup or alert appears.

## Current verification record

The 2026-10-04 modal/AJAX creation implementation was verified with `python manage.py check` (two existing W042 warnings), all 72 Django tests passing, `node --check static/js/blog.js`, and `git diff --check`. Added tests cover superuser-only modal visibility, ModelForm validation, JSON `201`/`400`/`403`, server-side permission revocation, POST-only behavior, CSRF enforcement, public search visibility of created records, and ignored server-managed inputs. A temporary Node VM check with mocked DOM/FormData/fetch/timers verified successful reset/close/toast and current-query refresh, duplicate-submit prevention, validation/authorization/server/network feedback with retained form state, CSRF inclusion, and submit-button recovery. This is not live-browser verification. Server-side Blog form tag stripping and manual browser/XSS checks remain outstanding. The records below describe earlier implementation stages.

The 2026-10-04 checklist review reflects the implemented AJAX list shell, manually composed JSON with aggregate and caller-specific star state, safe DOM rendering, and loading/error/retry/empty states. In this session, before this documentation-only update, `python manage.py check` completed with two existing W042 warnings, all 58 Django tests passed, and `node --check static/js/blog.js` passed. These commands were not rerun for this checklist update. Search/debouncing, AJAX creation, Blog form tag stripping, and live browser verification remain outstanding. The source review below is historical.

The 2026-10-04 search implementation was verified with `python manage.py check` (two existing W042 warnings), all 64 Django tests passing, and `node --check static/js/blog.js` passing. Tests cover partial/case-insensitive title matching, whitespace/empty queries, no matches, public search across all roles, star privacy, ordering, and escaped query restoration. A temporary Node VM harness using a transcription of the script and mocked DOM/timers/fetch passed 46 assertions for 300 ms debounce, cancellation, immediate submit, retry, query clearing, and history updates without navigation; this is not a live-browser check. AJAX creation, Blog form tag stripping, and live browser verification remain outstanding.

The 2026-10-03 source review found the following state at that time; this is historical static inspection, not a fresh runtime test:

- `/blog/` currently prepares and server-renders annotated BlogPost rows after a Django JSON serialize/deserialize round trip; it is not yet a shell-only AJAX list.
- `/api/blog/` currently uses Django serialization, does not accept a search query, and omits star count and current-user star state.
- `/blog/add/` currently provides the superuser's traditional create form; there is no Blog create modal or AJAX create endpoint in the route table.
- `BlogPostForm` does not currently strip tags from title/content.
- Current template autoescape and `linebreaks` protect server-rendered content, but the required JavaScript Blog renderer does not yet exist.
- The role baseline, JSON detail endpoint, Blog star route, and update/delete routes are present as described above.

Earlier documentation records 43 Django tests and related checks passing on 2026-09-28. Those historical results are not evidence that the Assignment 5 target has been implemented or that checks were rerun during this documentation update. Live browser verification remains outstanding.
