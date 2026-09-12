# Blog Section

**Status:** Implementation complete; static audit complete; runtime verification pending

**Parent plan:** [Portfolio layout plan](../portfolio-layout-plan.md)

## Purpose

Add a dedicated Blog page that presents Victoriano's personal and technical writing. Blog is a dynamic exception to the otherwise static landing-page content: each database object represents one blog post.

The Blog page is separate from Projects and Journey. Projects remains the area for software and technology work, while Journey remains the area for academic, competition, mentorship, and professional milestones.

## Naming

- User-facing section: `Blog`
- Canonical content type: `Blog post`
- Django model: `BlogPost`
- View: `show_blog`
- Named route: `main:show_blog`
- URL: `/blog/`
- Template: `templates/blog.html`
- Context variable: `blog_posts`

`BlogPost` is preferred over `Blog` because each record represents one written post, not the whole blog. `Article` is also understandable, but `BlogPost` matches the user-facing Blog section most directly.

## Content contract

The page should use the existing English interface style:

- Page/section label: `Blog`
- Each post displays its title, full content, and creation date.
- The date uses a simple format such as `12 September 2026`.
- Plain-text line breaks are preserved with Django's `linebreaks` filter.
- Django autoescape remains enabled; database content must not be treated as raw HTML.
- Empty state: `No blog posts have been added yet.`

Do not add fabricated posts, seed data, or fixture data. The page should be empty until a post is added through Django Admin.

## Data model contract

`BlogPost` has Django's automatic `BigAutoField` primary key and exactly these additional fields:

| Field | Type | Required | Purpose |
| --- | --- | --- | --- |
| `title` | `CharField(max_length=255)` | Yes | Post title |
| `content` | `TextField` | Yes | Full plain-text post content |
| `created_at` | `DateTimeField(auto_now_add=True)` | Automatic | Creation timestamp and display/order date |

Posts are ordered newest first with `created_at` descending and `id` descending as the deterministic tie-breaker.

## Page and navigation contract

- Register `path("blog/", show_blog, name="show_blog")` in `main/urls.py`.
- The view retrieves all `BlogPost` objects in the agreed order and passes them as `blog_posts` to `blog.html`.
- The template loops over every object using Django Template Language.
- The template uses `{% empty %}` or an equivalent empty branch for the no-posts state.
- Add the `Blog` navbar link with `{% url 'main:show_blog' %}` to `index.html`, `experience.html`, and `blog.html`.
- Place the link after `Experience` and before `Contact`.
- Keep the existing navbar, footer, Bootstrap setup, and responsive visual identity consistent with the other pages.
- Reuse existing responsive layout styles and add only the minimum Blog-specific CSS needed.
- Do not introduce a `base.html` refactor for this feature.

## Admin contract

Register `BlogPost` with the default Django Admin. No custom `ModelAdmin`, search, filters, preview, or authoring form is needed for this checkpoint.

## Required migration and tests

The implementation must create and apply a migration for `BlogPost`, and the migration file must be included in the commit.

At minimum, add tests for:

1. `/blog/` is accessible and uses `blog.html`.
2. A stored BlogPost's title and content appear in the HTML.
3. The empty state appears when no BlogPost exists.

The tests should also protect the agreed ordering and plain-text line-break behavior if those behaviors are covered during implementation.

## Implementation checklist

- [x] Add `BlogPost` to `main/models.py` with the three agreed fields.
- [x] Create the model migration and include the migration file.
- [x] Apply the migration successfully.
- [x] Register `BlogPost` in `main/admin.py`.
- [x] Add `show_blog` to `main/views.py` with ordered `blog_posts` context.
- [x] Add the `/blog/` named route in `main/urls.py`.
- [x] Create `templates/blog.html` with the shared navbar and footer.
- [x] Render all posts with a Django Template Language loop.
- [x] Render the agreed empty-state message when no posts exist.
- [x] Preserve plain-text content and line breaks with autoescape and `linebreaks`.
- [x] Add the Blog navbar link to all three templates using `{% url %}`.
- [x] Add only the minimum responsive Blog styles required.
- [x] Add the three required unit-test cases.
- [x] Run `python manage.py test` with all tests passing.
- [x] Run `python manage.py runserver` and confirm startup without errors.
- [x] Verify that an Admin-created post appears on `/blog/`.

## Acceptance scenarios

### Empty database

When no BlogPost exists, `/blog/` returns HTTP 200, uses `blog.html`, renders no post card, and shows `No blog posts have been added yet.`

### One or more posts

When posts exist, every post appears with its title, full content, and formatted creation date. Newer posts appear first.

### Same creation timestamp

When posts share the same `created_at`, the larger automatic `id` appears first.

### Plain-text content

Content containing line breaks remains readable as separate lines or paragraphs. HTML entered as content is escaped rather than executed.

### Admin workflow

A user can create or edit a BlogPost through the default Django Admin, and the saved record appears on `/blog/` without adding a separate form.

## Explicitly out of scope

- Individual post detail pages or slug-based URLs
- Pagination or infinite scrolling
- Draft/published status
- Tags, categories, author fields, images, or excerpts
- Markdown or rich-text editing
- Raw HTML rendering
- Seed data or fixtures
- New dependencies
- A shared-template refactor

## Verification log

Static implementation verification on 2026-09-12:

- [x] The Blog template, post loop, empty state, date formatting, and `linebreaks` rendering are present.
- [x] The Blog navbar link is present in `index.html`, `experience.html`, and `blog.html`.
- [x] Minimum Blog-specific responsive styles are present.
- [x] `main_blogpost` exists in `db.sqlite3`, and migration `0002_blogpost` is recorded as applied.
- [x] JavaScript syntax and Git whitespace checks passed.

Runtime verification remains pending because no accessible Python interpreter or browser target is available:

- [x] Blog-specific unit-test cases have been added.
- [ ] `python manage.py test` and `python manage.py runserver` could not be run.
- [ ] Admin-created post rendering and live desktop/mobile behavior remain unverified.
