# Projects: Pages, Authorization, and Stars

Status: Implemented, including AJAX listing/search and superuser create modal; automated verification recorded in repository notes; live browser verification remains pending.

Parent plan: [Portfolio layout and implementation](../portfolio-layout-plan.md)

## Scope and distinction

“Projects” appears in two separate parts of the product:

1. The static landing-page section at `/#projects` is a coming-soon placeholder with a link to `/projects/`.
2. The database-backed Project feature is implemented with list/detail pages, JSON reads, AJAX listing/search, create/update/delete actions, a superuser create modal, and stars.

This document describes the second feature. Its current implementation is found in `main/models.py`, `main/forms.py`, `main/views.py`, `main/urls.py`, `templates/project.html`, `templates/projects_form.html`, `templates/components/project_form_modal.html`, `static/js/projects.js`, `static/js/toast.js`, and the shared stylesheet.

## Data model and form

`Project` uses a UUID primary key and contains:

| Field | Type | Form writable | Purpose |
| --- | --- | --- | --- |
| `title` | `CharField(max_length=255)` | Yes | Project title and list search target. |
| `description` | `TextField` | Yes | Project description. |
| `tech_stack` | `CharField(max_length=255)` | Yes | Technology label displayed on the card. |
| `project_url` | `URLField(blank=True)` | Yes | Optional external project link. |
| `project_image_url` | `URLField(blank=True, max_length=500)` | Yes | Optional image URL. |
| `starred_by` | Many-to-many to Django `User`, blank allowed | No | Per-user star membership. |

`ProjectForm` excludes the primary key and `starred_by`, so editing Project content cannot directly change star membership.

The form strips HTML tags from `title`, `description`, and `tech_stack`; a title that becomes empty after stripping is rejected. The AJAX renderer builds card content using DOM APIs and `textContent` instead of interpolating Project text into HTML, preserving text-safe rendering for fetched records.

## Routes and page behavior

| URL | Name | Method/visibility | Behavior |
| --- | --- | --- | --- |
| `/projects/` | `main:show_projects` | Public GET | Shows projects, optional `?title=` case-insensitive title search, star counts and role-appropriate controls. |
| `/projects/<uuid:id>/` | `main:show_project_detail` | Public GET | Renders one project using `project.html` in detail mode. |
| `/projects/add/` | `main:create_project` | Superuser GET/POST | Form display and Project creation. |
| `/projects/add-ajax/` | `main:create_project_ajax` | Superuser POST | AJAX create endpoint used by the add-project popover; returns JSON success or validation errors. |
| `/projects/<uuid:id>/edit/` | `main:update_project` | Editor/superuser GET/POST | Form display and content update. |
| `/projects/<uuid:id>/delete/` | `main:delete_project` | Superuser POST | Deletes the Project and redirects to list. |
| `/projects/<uuid:project_id>/star/` | `main:toggle_star` | Authenticated POST | Atomically toggles current user's membership; redirects to list. |
| `/api/projects/` | `main:get_projects_json` | Public GET | JSON collection with optional title filter; includes star count and the requesting user's own star state when authenticated. |
| `/json/<uuid:id>/` | `main:show_json_by_id` | Public GET | One JSON Project or 404. |

The `/projects/` list loads asynchronously from `/api/projects/`. Search is debounced by 300 ms, can abort an in-flight superseded fetch, and updates the query string without full-page navigation. Loading, error/retry, and empty states are rendered. Superusers create from the listing popover/modal via AJAX; successful creation resets/closes the modal, shows a toast, and reloads the current filtered list. The traditional `/projects/add/` route remains available. Successful traditional form writes use redirects (Post/Redirect/Get). Unknown UUIDs return 404. Public JSON does not disclose user identities or individual star memberships; the list endpoint includes aggregate count and the authenticated caller's own membership state so the UI can show their control state.

## Authorization contract as implemented

| Capability | Anonymous | Authenticated regular user | Editor | Superuser |
| --- | --- | --- | --- | --- |
| Read Project HTML list/detail and JSON | Allow | Allow | Allow | Allow |
| Create | Login redirect | 403 | 403 | Allow |
| Update content | Login redirect | 403 | Allow | Allow |
| Delete | Login redirect | 403 | 403 | Allow |
| Star/unstar | Login redirect | Allow | Allow | Allow |

`Editor` means membership in the exact Django Group named `Editor`. It grants update authority only; superuser checks independently grant create/update/delete. Users are not automatically assigned Editor during registration. Django Admin permissions are separate from public-view role checks.

The `protected` decorator applies authentication, authorization, then allowed-method validation. Anonymous protected requests redirect to `main:login` with a `next` value; login validates that destination as local before redirecting. Authenticated unauthorized requests receive 403; authorized requests using unsupported methods receive 405. Delete and star endpoints are POST-only and templates include CSRF tokens.

## Star behavior and presentation

- A star is one membership between a Project and a User; the many-to-many join prevents duplicate pair memberships.
- Each authenticated user can toggle their own membership; consecutive toggles alternate starred/unstarred.
- The view wraps the read-and-change operation in a transaction and locks the selected Project row.
- List/detail rendering provides total star count and the current user's state. Anonymous visitors see the count and a login link instead of a mutation form.
- The star relation is not part of Project create/update forms or public JSON.
- Project create/delete controls are shown only to superusers; edit controls are shown to Editors/superusers.

## Verification history

The implementation plan's acceptance matrix was completed according to the historical repository verification log on 2026-09-28: 43 Django tests, project checks, migration checks, and local HTTP smoke checks passed. Live desktop/mobile visual review remains outstanding. This document is descriptive; consult current tests and source if implementation changes.
