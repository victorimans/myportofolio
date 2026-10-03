# Project agent instructions

## Documentation scope and repository facts

- If the user restricts a task to documentation, change only the requested Markdown (`.md`) files. Do not edit application code, templates, styles, scripts, configuration, or data.
- Before editing, inspect `git status` and preserve existing uncommitted user changes. Do not revert, stage, or otherwise modify unrelated changes.
- Treat current source code as authoritative for implemented behavior; treat `CONTEXT.md` as the domain vocabulary and `docs/Portofolio-layout-plan/portfolio-layout-plan.md` plus its section plans as implementation notes that may need reconciliation.
- Keep claims about tests, browser checks, or runtime verification tied to recorded evidence; do not imply historical checks were rerun.

### Current feature distinctions

- The landing-page Projects and Journey sections are static coming-soon content. Database-backed Projects are a separate feature at `/projects/`; Experience is separately displayed at `/experience/`.
- Project listing data is loaded through `/api/projects/` and `static/js/projects.js`. Title search is debounced (300 ms), fetches may be aborted, and list state includes loading, error/retry, and empty states. Superusers create through the AJAX popover/modal endpoint `/projects/add-ajax/`; the traditional `/projects/add/` route also remains present.
- Project input strips HTML tags in `ProjectForm`; dynamically rendered project-card text uses text-safe DOM construction. Preserve this security behavior when documenting the form or renderer.
- Superusers create/delete Project and BlogPost records; membership in the exact `Editor` group grants update; authenticated users can star/unstar both Projects and Blog posts. Registration does not assign Editor membership.
- Public Project and Blog JSON does not expose individual star membership or account details.
- Experience is a database-backed public listing and has no public create/update/delete route in the current application.

## grill-with-docs

When the user asks for `grill-with-docs`, asks to be grilled, or asks to stress-test a plan or design:

1. Use the `grilling` skill to interview the user in numbered rounds.
2. Ask the whole current decision frontier in each round, give a recommended answer for every question, and wait for the user before continuing.
3. Find facts from the repository yourself; ask the user only for decisions.
4. Use the `domain-modeling` skill alongside the interview. Challenge ambiguous terms, test decisions with concrete scenarios, and compare the model against the code.
5. Do not implement the plan until the user confirms that shared understanding has been reached.
6. When a domain term is resolved, update the repository glossary in `CONTEXT.md`. Create that file only when there is a term worth recording.
7. Create an ADR only for a hard-to-reverse, surprising trade-off. Create `docs/adr/` only when the first ADR is needed.
