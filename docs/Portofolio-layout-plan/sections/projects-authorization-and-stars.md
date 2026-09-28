# Projects: Authorization, Editor, and Stars

Status: Specification agreed; implementation is not part of this document task

Parent plan: [Portfolio layout plan](../portfolio-layout-plan.md)

## Purpose and scope

Specify the access-control and interactive-star behavior for the database-backed Projects section, continuing the authentication pattern established in Tutorial 04. This document is an implementation-ready contract for a later coding task. It does not claim that the specified behavior is already implemented.

The scope is the `Project` resource and its HTML and JSON read interfaces. The database-backed Projects route is distinct from the static landing-page Projects placeholder described in the parent layout plan; this specification does not itself authorize replacing that placeholder or changing the landing-page layout. Blog posts, Experience records, Mahasiswa records, registration policy, account lifecycle, and general Django Admin CRUD behavior are outside this feature's scope. The role called **Project owner** below means a superuser account, as required by the assignment; it does not mean per-record ownership.

## Current repository baseline (checked 2026-09-28)

These are observations of the repository, not acceptance criteria or claims of completion:

- `main.models.Project` already has `starred_by = ManyToManyField(User, related_name="starred_projects", blank=True)`.
- Migration `main/migrations/0005_project_starred_by.py` already exists. A future implementation task should inspect migration state and use `makemigrations --check` rather than duplicate this field or migration.
- Project create and delete views currently check `is_superuser`; create accepts GET/POST and delete accepts POST.
- The current `login_user` view redirects to the landing page after authentication and does not appear to honor `next`; the agreed contract requires safe continuation to the protected local destination.
- There is no Project update route/view in `main/urls.py` at this baseline.
- `toggle_star` currently uses `login_required`, but its view is not restricted to POST. The Projects template includes a CSRF token and displays a count, but its title currently exposes the usernames of users who starred a project. That disclosure is not allowed by this specification.
- The Projects template shows create/delete controls only for superusers and currently renders the star POST form regardless of authentication state. No Editor role or update control is present at this baseline.
- The URL configuration has a public Projects HTML list but no dedicated Project detail HTML route. The assignment explicitly requires list and detail pages to remain publicly readable, so a future implementation must provide a public detail HTML route if no equivalent route exists by then. The JSON detail route is present.
- Project list and detail JSON views serialize model data. Their public contract must be checked before changes; star membership must not be exposed.
- `ProjectForm` contains the content fields `title`, `description`, `tech_stack`, `project_url`, and `project_image_url`, and does not include `starred_by`.
- Existing tests currently expect the JSON serializer to contain `starred_by` usernames and expect an authenticated GET to the star route to redirect rather than return 405. Those expectations conflict with the agreed contract below and must be revised in a future implementation task.

## Domain language

Use the canonical definitions in the root [`CONTEXT.md`](../../../CONTEXT.md): Project, Project owner, Editor, and Star. In particular, star membership is an interaction relationship, not editable Project content.

## Role and capability contract

Every read operation is public. Project content is readable whether or not a visitor is authenticated. All authenticated account types can star and unstar Projects. Only the roles below may change Project content:

| Capability | Anonymous visitor | Authenticated user | Editor | Superuser (Project owner) |
|---|---:|---:|---:|---:|
| Read Project list and detail HTML | Allow | Allow | Allow | Allow |
| Read public Project JSON list/detail | Allow | Allow | Allow | Allow |
| Create Project | Login redirect | 403 | 403 | Allow |
| Update Project content | Login redirect | 403 | Allow | Allow |
| Delete Project | Login redirect | 403 | 403 | Allow |
| Star/unstar Project | Login redirect | Allow | Allow | Allow |

The Editor role is granted by membership in the Django Group named `Editor`, managed through Django Admin. Group membership grants update authority only. It does not grant create, delete, superuser, account-management, or star-membership editing authority. Superuser capabilities are based on `is_superuser`; Group membership does not reduce or expand that rule.

Role membership is evaluated at request time: adding a user to `Editor` enables permitted updates on subsequent requests; removing membership revokes that access. A superuser remains authorized for owner actions regardless of Editor Group membership.

The project does not need a per-Project owner field for this requirement. “Project owner” is the portfolio-maintainer role represented by superuser status.

## Server-side authorization requirements

1. Enforce authorization in each server-side view handling create, update, delete, and star. Template conditionals are a presentation aid and never the security boundary. Keep Project list and detail reads public. If no HTML detail route exists, add one as part of a future implementation and keep it public; the detail view must not require login.
2. Separate form display from state change: an authorized GET to a create or update form may return 200, and a permitted POST may create/update. An authorized GET to delete or toggle-star does not perform the action and returns 405. Delete and star are POST-only.
3. For an anonymous visitor requesting any protected action endpoint, authentication takes precedence: redirect to the configured login route and preserve a safe `next` destination for the requested action, including requests with an unsupported method. After successful login, return the user to that safe local destination; reject external or otherwise unsafe `next` values and fall back to the normal post-login destination. For authenticated callers, authorization is checked before method acceptance so an unauthorized user receives 403, while an authorized caller using an unsupported method receives 405. In every case an unsupported method must never mutate state.
4. For an authenticated user without the required capability, return HTTP 403 for both form GET and mutation POST, not a login redirect. Do not save or delete anything before authorization succeeds.
5. A supported method used by an authenticated unauthorized user still returns 403; method restrictions must not become a bypass. For an authorized caller, an unsupported method returns HTTP 405. Invalid form data returns the form with validation errors and changes no data.
6. The star endpoint requires authentication and POST. Django CSRF middleware must validate the submitted token. A rejected method or CSRF request must not change star membership.
7. Resolve a Project by its existing identifier and return 404 for an unknown identifier; authorization must not disclose or mutate a nonexistent record. Do not rely on a project ID in a form as proof of access.
8. Validate update input through the Project form/model validation path. The set of writable fields is the Project content form's fields; `starred_by` is not writable through create/update forms, crafted payloads, or ordinary content editing.
9. On successful create, update, delete, and star POST, redirect to the Projects list (Post/Redirect/Get). Invalid form submissions render the relevant form and do not redirect as if a change succeeded.
10. Treat each star POST as one atomic membership toggle. The database relation must prevent duplicate `(Project, User)` memberships; failures must not leave a partially changed state.

## Group and administration requirements

- Provide a Django Group named exactly `Editor` as the role marker.
- An administrator assigns or removes user membership through Django Admin's Group/user administration interface.
- Document the setup path for environments where the Group has not yet been created (for example, create it through Admin or an idempotent data/setup mechanism chosen by the implementer). Do not make registration automatically grant Editor.
- Verify the role through server-side membership in the exact `Editor` Group; do not silently substitute an unrelated permission or trust submitted form values/client-controlled role flags.
- Keep ordinary user and superuser star capability independent of Editor membership.

## Star behavior and presentation

### State transition

For one `(Project, User)` pair, star is a two-state toggle:

- not starred → starred;
- starred → not starred.

The relationship must enforce at most one active star per user per Project. Repeated requests are toggles, so two valid consecutive requests restore the original state. All authenticated users, including Editors and superusers, may perform this action. Anonymous visitors are sent to login and must not mutate state.

Use the existing `Project.starred_by` relation if it remains consistent with the baseline. The data model must retain a ManyToMany relation to Django's User model and migration state must be applied. Do not create a second star store.

### HTML contract

On each Project card/detail representation where stars are available:

- Show the total number of stars.
- For an authenticated user, show whether that user has starred the Project and provide a POST form to star/unstar it. The visible action label/state should reflect the user's current state.
- Include `{% csrf_token %}` in the POST form.
- For an anonymous user, show the count and provide a login path or login link instead of an actionable star POST control.
- For a Project with zero stars, display `0` rather than omitting the count; pluralization/accessibility text should remain clear for zero, one, and multiple stars.
- If a Project is deleted, its star associations must be removed by the relation's normal referential behavior; no orphaned membership may remain.
- Never show a list of star-giver usernames, email addresses, or other identifying data in page text, attributes, or tooltips.
- After a successful toggle, return to the Projects list (preserving a safe local return location only if deliberately supported and validated). The baseline agreed behavior is redirect to the Projects list.
- Ensure template context exposes the count and current user's membership efficiently and correctly for each Project. Avoid N+1 query growth where practical.

The Project content controls follow the role matrix: create and delete controls are visible only to superusers; update controls are visible to Editors and superusers. A hidden control does not replace view authorization.

## Public JSON/API contract

- Keep the existing public Project list and detail JSON routes available to anonymous and authenticated callers.
- Preserve the existing response shape, identifiers, Project content fields, status behavior, and filtering behavior required by the Tugas 3 client contract.
- Deliberately exclude the `starred_by` relation from JSON even if an existing response currently includes it. This is a privacy correction and the sole specified response-field removal; do not serialize star membership, user IDs, usernames, email addresses, or other per-user membership data.
- The star count and current-user star status are HTML presentation requirements; do not add them to JSON under this task unless a later API specification explicitly requests them.
- Verify the actual serializer output rather than assuming ManyToMany relations are included or excluded by default.
- Do not expose write operations through JSON as part of this scope.

## Template and navigation requirements

- Public read controls remain available to all visitors.
- Show Add Project only to superusers.
- Show Edit Project only to Editor members and superusers.
- Show Delete Project only to superusers.
- Show the authenticated star/unstar POST control to all authenticated account types; show the anonymous login route/link otherwise.
- Use POST forms with CSRF tokens for delete and toggle-star controls; do not use destructive GET links.
- Keep links and buttons keyboard accessible and make the star state understandable without relying only on color or a decorative star glyph.

## Acceptance matrix and verification scenarios

Run each applicable case against the server-side route, not only by inspecting rendered controls. Use separate anonymous, ordinary-user, Editor, and superuser test clients.

| Scenario | Expected result |
|---|---|
| Anonymous GET Project list/detail HTML | 200; content visible |
| Anonymous GET list/detail JSON | 200; public content only |
| Ordinary user GET list/detail HTML/JSON | 200; same public visibility |
| Editor GET list/detail HTML/JSON | 200; same public visibility |
| Superuser GET list/detail HTML/JSON | 200; same public visibility |
| Anonymous GET/POST create, update, or delete | Redirect to login with safe `next`; no mutation |
| Anonymous GET or POST star | Redirect to login with safe `next`; no mutation |
| Anonymous protected request after valid login | Return to safe local `next` target; external/unsafe `next` falls back to standard destination |
| Authorized superuser GET create form | 200; form displayed; no Project created |
| Authorized Editor GET update form | 200; form displayed; Project unchanged |
| Ordinary user GET or POST create | 403; no Project created |
| Ordinary user GET or POST update | 403; Project unchanged |
| Ordinary user GET or POST delete | 403; Project remains |
| Editor GET or POST create | 403; no Project created |
| Editor GET or POST update valid Project content | Success; allowed content fields change |
| User added to Editor Group then requests valid update | Update allowed |
| Editor membership removed then requests update | 403; Project unchanged |
| Superuser not in Editor Group requests update/create/delete | Allowed according to superuser capabilities |
| Editor update attempt to alter `starred_by` via submitted data | Relation unchanged; field is not writable |
| Editor GET or POST delete | 403; Project remains |
| Superuser create valid Project | Success; Project created |
| Superuser update Project content | Success; allowed content fields change |
| Superuser delete via POST | Success; Project removed |
| Authenticated user, Editor, or superuser POST star when not starred | One relation added; count increases by one; UI state becomes starred |
| Same account POST star again | Relation removed; count decreases by one; UI state becomes unstarred |
| Same account repeats a star operation on another Project | Each Project has an independent relationship |
| Any account submits star form without valid CSRF token using a CSRF-enforcing test client | Rejected by CSRF protection; relation unchanged |
| Any role submits delete form without valid CSRF token using a CSRF-enforcing test client | Rejected by CSRF protection; Project remains |
| Anonymous POST star | Login redirect; relation unchanged |
| Authenticated authorized caller uses unsupported method on star or delete | 405; no mutation |
| Authenticated ordinary user uses unsupported method on delete/star | 403 because authorization denial takes precedence; no mutation |
| Authenticated superuser uses GET on delete or star | 405; no mutation |
| Authenticated supported GET form request to create/update by a permitted role | 200; form only, no mutation |
| Authenticated unsupported method to a create/update endpoint | 405; no mutation |
| Permitted role submits invalid create/update form | Form validation errors; no record or field changes |
| Authenticated ordinary user attempts protected edit/delete through crafted direct URL | 403; no mutation, regardless of hidden controls |
| Unknown Project identifier | 404; no mutation |
| Project JSON list/detail contains star/user data | Must not occur; assert absence of `starred_by`, star-giver usernames, user IDs, emails, and other membership data |
| Project JSON list filtering by title | Existing Tugas 3 filtering behavior remains intact |
| Project JSON detail for a known ID | 200; one public Project record; no star membership data |
| Project JSON detail for an unknown ID | 404 |
| Rendered Projects page for anonymous user | Count is visible, star action directs to login, no create/update/delete controls |
| Rendered Projects page for ordinary user | Star controls visible; no create/update/delete controls |
| Rendered Projects page for Editor | Star and update controls visible; no create/delete controls |
| Rendered Projects page for superuser | Star, create, update, and delete controls visible |
| Public Project detail HTML for each role | 200; Project content visible without login |
| Administrator adds/removes account from `Editor` in Django Admin | Membership is saved and reflected in subsequent authorization checks |
| Newly registered account without Editor assignment | Ordinary-user capabilities only |
| Superuser is also/not in Editor Group | Same superuser capabilities in both cases |

## Data and migration checks

- Confirm the User-to-Project star relation is represented once and supports at most one membership per user/project pair.
- Confirm the migration files and applied database schema agree. On this baseline, migration `0005_project_starred_by.py` already exists, so inspect before generating any migration.
- Run `python manage.py makemigrations --check` and `python manage.py migrate --check` where supported by the Django version; apply pending migrations in the intended environment.
- Existing Projects must remain readable and retain valid star memberships after migration/deployment.

## Definition of done for a future implementation

- [ ] Role checks implement the matrix server-side for every action route.
- [ ] `Editor` role is manageable in Django Admin and does not grant create/delete.
- [ ] A Project update route and form support the defined content fields for Editor and superuser.
- [ ] All state changes use POST and CSRF validation; unsupported methods return 405.
- [ ] Successful state changes use redirects to the Projects list; invalid forms preserve entered values/errors and do not mutate records.
- [ ] CSRF rejection is verified with Django's test client configured to enforce CSRF checks, rather than relying on its default test-only bypass.
- [ ] Login safely honors a valid local `next` destination for protected actions and rejects unsafe external destinations.
- [ ] Authorized GET requests to create/update render forms without mutating state; valid POST changes only allowed content; invalid POST leaves data unchanged.
- [ ] Star count and current-user state are correct for anonymous and authenticated rendering; usernames are never disclosed.
- [ ] Project JSON remains public and preserves Tugas 3 Project content/filtering contract; `starred_by` is intentionally excluded as a privacy correction.
- [ ] Template controls match role capabilities while backend checks independently enforce them.
- [ ] Acceptance scenarios above pass, migrations are consistent, and `python manage.py check` passes.
- [ ] `python manage.py runserver` starts without errors and the key public/authenticated routes render successfully.

## Explicit non-goals

- Changing authentication backend, registration fields, or login/logout design beyond preserving the redirect behavior needed for protected actions.
- Applying this role model to BlogPost, Experience, Mahasiswa, or Django Admin content workflows.
- Introducing individual Project ownership or per-user project visibility.
- Publishing the identities of users who starred a Project.
- Building an API write endpoint or changing the Tugas 3 JSON contract beyond preventing sensitive data exposure.
