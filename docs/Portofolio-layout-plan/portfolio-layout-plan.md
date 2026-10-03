# Portfolio Layout and Implementation

Status: Core implementation is present across the landing page and database-backed pages; automated verification is recorded, while live browser/responsive verification remains outstanding.

Last reconciled with the repository: 2026-10-03

## Scope and implementation map

This document records the implemented portfolio behavior in `main/`, `portofolio/`, `templates/`, and `static/`. It describes the current repository state; it is not a list of proposed work. The source files are the implementation authority if they change.

| Area | Implemented files | Current responsibility |
| --- | --- | --- |
| Django project configuration | `portofolio/settings.py`, `portofolio/urls.py`, `portofolio/views.py`, `portofolio/asgi.py`, `portofolio/wsgi.py` | Project settings and root routing. Root URL configuration delegates to `main.urls`; Django Admin is mounted at `/admin/`. |
| App routes and behavior | `main/urls.py`, `main/views.py`, `main/forms.py` | Landing, authentication, Projects, Experience, Blog, mutation actions, and read-only JSON routes. |
| Data and administration | `main/models.py`, `main/admin.py`, `main/migrations/` | Experience, Project, BlogPost, Mahasiswa records, relations, migrations, and default Django Admin registration. |
| Shared page shell | `templates/base.html` | Document head, Bootstrap navbar, messages, footer, shared scripts, and asset loading. |
| Landing page | `templates/index.html` | Static Profile, About, Skills, Projects/Journey placeholders, and Contact sections. |
| Database-backed pages | `templates/project.html`, `templates/experience.html`, `templates/blog.html` | Dynamic Project list/detail, Experience list, and Blog list pages. |
| Forms and accounts | `templates/projects_form.html`, `templates/components/project_form_modal.html`, `templates/blog_form.html`, `templates/login.html`, `templates/register.html` | Project/Blog CRUD forms, AJAX Project modal, and account flows. |
| Presentation and behavior | `static/css/style.css`, `static/js/main.js`, `static/js/projects.js`, `static/js/toast.js`, `static/img/Victoriano_Iman_Santosa.jpg` | Shared visual system, responsive styles, AJAX Project listing/form behavior, toast notifications, sakura effect, clipboard feedback, and profile image. |

## Route map

Routes are mounted under the root URL by `portofolio/urls.py` and namespaced as `main`.

| URL | Name | Behavior / template |
| --- | --- | --- |
| `/` | `main:show_main` | Static portfolio landing page, `index.html`. |
| `/register/` | `main:register` | Django user registration, `register.html`. |
| `/login/` | `main:login` | Login, safe local `next` handling, `login.html`. |
| `/logout/` | `main:logout` | POST-only logout. |
| `/projects/` | `main:show_projects` | Public database-backed Project listing and title search, `project.html`; listing data is fetched asynchronously from `/api/projects/`. |
| `/projects/add/` | `main:create_project` | Superuser Project create form. |
| `/projects/add-ajax/` | `main:create_project_ajax` | Superuser, POST-only Project create endpoint used by the listing modal; returns JSON success/errors. |
| `/projects/<uuid:id>/` | `main:show_project_detail` | Public Project detail rendered by `project.html`. |
| `/projects/<uuid:id>/edit/` | `main:update_project` | Editor/superuser Project update form. |
| `/projects/<uuid:id>/delete/` | `main:delete_project` | Superuser, POST-only deletion. |
| `/projects/<uuid:project_id>/star/` | `main:toggle_star` | Authenticated, POST-only Project star toggle. |
| `/experience/` | `main:show_experience` | Database-backed Experience listing, `experience.html`. |
| `/blog/` | `main:show_blog` | Public database-backed BlogPost page, `blog.html`; Assignment 5 target is a shell with AJAX-loaded list, title search, and superuser create modal. Current source still server-renders the list. |
| `/blog/add/` | `main:create_blog` | Current traditional superuser BlogPost create form; target AJAX modal flow may retain this route only for compatibility. |
| `/blog/add-ajax/` | Planned Assignment 5 route | Target superuser-only POST create endpoint returning JSON with 201/400/403 responses; not present in current source. |
| `/blog/<int:id>/edit/` | `main:update_blog` | Editor/superuser BlogPost update form. |
| `/blog/<int:id>/delete/` | `main:delete_blog` | Superuser, POST-only BlogPost deletion. |
| `/blog/<int:blog_id>/star/` | `main:toggle_blog_star` | Authenticated, POST-only BlogPost star toggle. |
| `/api/projects/` | `main:get_projects_json` | Public Project JSON collection; optional case-insensitive title filtering; includes total star count and, for authenticated callers, their own starred state, but no user identities. |
| `/json/<uuid:id>/` | `main:show_json_by_id` | Public Project JSON detail. |
| `/api/blog/` | `main:get_blog_json` | Current public BlogPost JSON collection; Assignment 5 target is manually composed JSON with title filtering, star_count, and caller-specific is_starred. Current source still uses Django serialization and omits these fields. |
| `/api/blog/<int:id>/` | `main:show_blog_json_by_id` | Public BlogPost JSON detail. |
| `/admin/` | Django Admin | Admin site with registered app models. |

## Landing page structure

`templates/index.html` extends `base.html` and contains one rendered landing page with these anchors in order:

1. **Profile (`#profile`)** — name, Computer Science / Universitas Indonesia kicker, profile image, bio, NPM, degree program, and a Download CV link to a shared Google Drive PDF. The GitHub, LinkedIn, and email links in the Profile markup are currently inside an HTML comment; those channels are live in Contact. There is no Download CV item in the shared navbar.
2. **About (`#about`)** — static English narrative and a Focus panel with Problem-solving, Teaching & mentorship, and Software, technology & impact.
3. **Skills (`#skills`)** — three capability panels and six contextual skills spanning problem-solving/competitive programming, teaching/mentorship, and software/technology.
4. **Projects (`#projects`)** — honest coming-soon copy plus a link to the dynamic `/projects/` page. This is distinct from the Project model and its CRUD/star workflow.
5. **Journey (`#journey`)** — honest coming-soon copy. There is no Journey model or dynamic Journey page currently implemented.
6. **Contact (`#contact`)** — email CTA with mailto and copy-email actions; topic labels; LinkedIn, GitHub, Codeforces, AtCoder, TLX, and Instagram grouped by purpose.

The landing page receives its identity facts and bio from `show_main` in `main/views.py`; the rest of these sections are template content rather than database records.

## Shared shell and visual behavior

`base.html` is the root template for all page templates. It provides:

- Bootstrap 5.3.3 CSS/JS, Space Grotesk from Google Fonts, Font Awesome 6.6.0, and `static/css/style.css`;
- a fixed responsive navbar linking to landing-page anchors and the Projects, Experience, Blog, Login, and Register routes;
- username and POST Logout controls for authenticated users, or Login/Register links for anonymous visitors;
- an accessible message region for Django messages;
- a footer with current year, portfolio identity, university affiliation, and Back to profile anchor;
- the sakura background container and shared `static/js/main.js` behavior.

The CSS uses a warm cream/paper, brown, purple, pink, and ink palette, a 960px content width, fixed-navbar spacing/anchor offset, shared focus-visible outlines, and a full-height flex body that pushes the footer down on short pages. The landing Profile is a two-column desktop composition that stacks at narrower widths. Shared section, card, Blog, Project, Experience, forms, navigation, footer, and contact styles live in the same stylesheet. The JavaScript skips petal generation when `prefers-reduced-motion: reduce` is active and handles Contact copy-email feedback with Clipboard API and a fallback.

The previous layout notes that claim a complete contrast audit or manual live responsive QA should be treated as desired checks, not verified evidence: no browser verification is recorded here.

## Data model and content lifecycle

| Model | Current fields/behavior | Rendered surface |
| --- | --- | --- |
| `Experience` | UUID primary key; title, description, category (internship, research, volunteer, part-time, full-time, freelance), optional thumbnail URL, automatic start timestamp, optional end timestamp; `is_ongoing` derives from missing end time. | Public `/experience/` list; ongoing/finished status. No public create/update/delete form is defined in the current routes. |
| `Project` | UUID primary key; title, description, tech stack, optional project URL and image URL; many-to-many `starred_by` relation to Django User. | Public list/detail and JSON, superuser creation/deletion, Editor/superuser update, authenticated star toggle. |
| `BlogPost` | Automatic integer key; title, text content, category (`ai`, `dsa`, `web-development`, `career`, `personal`), optional picture URL, automatic creation timestamp, many-to-many `starred_by` relation to Django User; newest-first order with id tie-break. | Public list and JSON; superuser create/delete, Editor/superuser update, authenticated star toggle. |
| `Mahasiswa` | `nama` and `npm`. | Registered in Django Admin; no portfolio route/template currently uses it. |

Project forms write title, description, tech stack, project URL, and image URL. `ProjectForm` strips HTML tags from title, description, and tech stack and rejects a title that is empty after stripping; the AJAX card renderer inserts text through text-safe DOM APIs. The listing fetches JSON asynchronously, debounces title-search input by 300 ms, aborts superseded fetches, updates the query string without navigation, and exposes loading, error/retry, and empty states. The superuser popover modal submits to `/projects/add-ajax/`, shows field/server errors, and refreshes the current listing after success; the traditional `/projects/add/` route remains available. Blog forms write title, content, category, and picture link; id and creation time are server-managed. Blog list view uses the public JSON serialization/deserialization flow before rendering. Project and Blog stars are separate relations and separate POST routes.

## Authorization behavior

The shared `protected` wrapper in `main/views.py` redirects anonymous users to the named login route with the requested local path as `next`; after authentication, `login_user` validates the destination against the current host. For authenticated users, role authorization is checked before method validation; unauthorized accounts receive 403 and authorized callers using unsupported methods receive 405.

| Operation | Anonymous | Authenticated regular user | Editor group | Superuser |
| --- | --- | --- | --- | --- |
| Public reads (landing, Projects, Experience, Blog, JSON) | Allow | Allow | Allow | Allow |
| Create Project / BlogPost | Login redirect | 403 | 403 | Allow |
| Update Project / BlogPost | Login redirect | 403 | Allow | Allow |
| Delete Project / BlogPost | Login redirect | 403 | 403 | Allow |
| Star/unstar Project or BlogPost | Login redirect | Allow | Allow | Allow |

`Editor` is an exact Django Group membership check and grants update only in the public Project/Blog workflows. Registration does not assign the role. Create/delete controls are superuser-only, edit controls appear for Editors and superusers, and stars appear to authenticated visitors. Mutation forms use POST and CSRF tokens. Django Admin remains a separate staff/model-permission surface. The Project collection JSON includes star count and only the requesting authenticated user's own star state; it does not reveal star-user identities. Blog collection JSON exposes post content fields only, not star counts, membership, or account details. Blog currently has star behavior in code despite an older Blog contract document that states no Blog stars; the current implementation in models, views, URLs, and template is authoritative and the documentation must reflect it.

## Sub-plan index

- [x] [About section](sections/about.md) — implemented; narrative length and current copy must be checked against the live template when copy changes.
- [x] [Skills section](sections/skills.md) — implemented as three panels with six items.
- [x] [Projects and Journey placeholders](sections/projects-and-journey-coming-soon.md) — implemented on the landing page; Projects links to the separate dynamic Project page.
- [x] [Contact section](sections/contacts.md) and [Contact redesign proposal](sections/contact-redesign-proposal.md) — redesign is implemented; current copy and channel groups are recorded here.
- [ ] [Blog section](sections/blog.md) — documents current behavior and Assignment 5 AJAX/search/modal/XSS target; AJAX list/create and server-side tag stripping remain unimplemented in current source.
- [x] [Projects authorization and stars](sections/projects-authorization-and-stars.md) — UUID-backed public detail/list, role-gated management, JSON privacy, and star behavior are implemented.

## Verification record

Repository documentation records these automated checks on 2026-09-28: Django project checks, 43 tests, migration checks, and local HTTP smoke checks passed. Earlier section notes also report JavaScript syntax and copy-email smoke checks. Treat these as historical logs, not a fresh run for this documentation-only reconciliation.

Still outstanding in the repository notes:

- live browser inspection at desktop and mobile widths, including collapsed navigation and all page templates;
- visual contrast verification across all current page components;
- manual clipboard behavior in an actual browser.

## Source of truth / known doc drift resolved here

- The landing-page Projects and Journey areas are static placeholders; Project records are served separately at `/projects/`.
- Experience is a separate database-backed route, not a populated Journey section.
- Download CV is present in Profile; the shared navbar does not currently include it despite older layout-plan requirements.
- Project and Blog stars both exist in current models/templates/views. Older Blog sub-plan statements declaring no stars are stale and are being aligned to the actual project.
- Blog and Project create/delete are superuser-only; Editor membership enables updates; all authenticated accounts can toggle stars.
- Contact includes Codeforces, AtCoder, TLX, and Instagram in addition to email, LinkedIn, and GitHub.
