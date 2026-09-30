# Blog: Pages, Content, Authorization, and Stars

Status: Implemented; automated verification recorded 2026-09-28; live browser verification remains pending.

Parent plan: [Portfolio layout and implementation](../portfolio-layout-plan.md)

## Purpose and routes

Blog is a dedicated database-backed page, separate from the static landing page. Blog posts are public and mutations are role-gated.

| URL | Name | Behavior |
| --- | --- | --- |
| `/blog/` | `main:show_blog` | Public BlogPost list at `templates/blog.html`. |
| `/blog/add/` | `main:create_blog` | Superuser GET/POST create form at `templates/blog_form.html`. |
| `/blog/<int:id>/edit/` | `main:update_blog` | Editor/superuser GET/POST update form. |
| `/blog/<int:id>/delete/` | `main:delete_blog` | Superuser POST-only delete. |
| `/blog/<int:blog_id>/star/` | `main:toggle_blog_star` | Authenticated POST-only star toggle. |
| `/api/blog/` | `main:get_blog_json` | Public JSON collection. |
| `/api/blog/<int:id>/` | `main:show_blog_json_by_id` | Public JSON detail or 404. |

All complete pages extend `templates/base.html`, which owns the document structure, shared assets, navbar, messages, footer, and scripts. The Blog list obtains data through the JSON serialization/deserialization flow before rendering.

## Data and rendering contract

`BlogPost` has an automatic integer primary key and these fields:

| Field | Type | Form writable | Purpose |
| --- | --- | --- | --- |
| `title` | `CharField(max_length=255)` | Yes | Post title. |
| `content` | `TextField` | Yes | Plain-text post content. |
| `category` | `CharField(max_length=30)` | Yes | One of AI, DSA, Web Development, Career, Personal; default `ai`. |
| `picture_link` | Optional URL field | Yes | Optional post image. |
| `created_at` | Automatic creation timestamp | No | Visible date and ordering. |
| `starred_by` | Many-to-many to Django `User` | No | Per-user star membership. |

Posts order by `-created_at`, then `-id`. The page renders title, full content, date, category, optional image, and an empty state (`No blog posts have been added yet.`). Content uses Django `linebreaks` while normal template autoescape remains enabled. JSON includes public post fields (`title`, `content`, `category`, `picture_link`, `created_at`); it does not expose star membership or account data.

`BlogPostForm` only writes `title`, `content`, `category`, and `picture_link`. Create/update forms use POST and CSRF tokens, show validation errors, and preserve `created_at`. Valid create/update/delete redirects to `/blog/` with a success message. Delete is not a state-changing GET.

## Authorization and Editor role

| Capability | Anonymous | Authenticated regular user | Editor | Superuser |
| --- | --- | --- | --- | --- |
| Read Blog HTML and JSON | Allow | Allow | Allow | Allow |
| Create BlogPost | Login redirect | 403 | 403 | Allow |
| Update BlogPost content | Login redirect | 403 | Allow | Allow |
| Delete BlogPost | Login redirect | 403 | 403 | Allow |
| Star/unstar BlogPost | Login redirect | Allow | Allow | Allow |

`Editor` is membership in the exact Django Group named `Editor`; it grants update authority only. Registration does not assign this group. Superuser status grants create/update/delete. Django Admin access remains governed independently by staff status and model permissions.

`protected` checks authentication, capability, then method. Anonymous protected requests redirect to login with a safe local `next`; unsafe external destinations are rejected by the login view. Authenticated users without capability receive 403. Permitted users using unsupported methods receive 405. Create/update support GET and POST; delete and star support POST only. State-changing forms use CSRF tokens.

## Star behavior

The current implementation includes a `BlogPost.starred_by` many-to-many relation, `/blog/<int:blog_id>/star/`, and star controls on each rendered post. Authenticated users toggle their own membership; the view performs the operation transactionally and redirects to the Blog list. The template displays total count and current-user state to signed-in users, and count plus a login-to-star link to anonymous visitors. Star membership is not editable through `BlogPostForm` or exposed by JSON.

This behavior is important documentation alignment: earlier drafts in this folder described a Blog domain with no stars and suggested removing the relation/migration. Those statements do not match the current source and are superseded by the implementation described here.

## Admin and content workflow

`BlogPost` is registered with default Django Admin in `main/admin.py`. The public workflow and Admin are distinct entry points. The public Blog page remains readable when empty and no fabricated seed posts are required. The navbar's Blog link in `base.html` points to the list route.

## Verification history

The repository's historical log records Blog checks and workflows, then the combined role-based feature suite on 2026-09-28 (43 tests), migration checks, Django checks, and local `/blog/` HTTP response as passing. The actual schema includes Blog stars (migration sequence through `0008_blogpost_starred_by.py`); the older proposed migration-removal plan is obsolete. Browser responsive and visual review remains outstanding.
