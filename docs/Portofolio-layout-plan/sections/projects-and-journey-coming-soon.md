# Projects and Journey Sections

Status: Implemented in `templates/index.html`; live browser verification pending

Parent plan: [Portfolio layout plan](../portfolio-layout-plan.md)

## Purpose

Keep the Projects and Journey sections visible on the static landing page while explaining where real content is available or why it is not ready. The sections should communicate this honestly without fabricated records.

## Agreed direction

- Change only Projects and Journey; leave Contact unchanged.
- Keep the existing navigation anchors working.
- Use English copy to match the rest of the portfolio.
- Use one shared centered `coming-soon-panel` design.
- Match the existing cream, brown, purple, and pink visual identity.
- Projects includes a functional link to the separate database-backed `/projects/` page.
- Journey remains a static placeholder; detailed milestones are not yet represented by a Journey model or route.

## Content

### Projects

Explore my projects.

I'm building and documenting projects that reflect how I learn, solve problems, and explore technology. The panel links to the implemented Projects page.

### Journey

My journey is still unfolding.

Academic, competition, mentorship, and professional milestones will be added here soon.

## Implementation

- Keep the `#projects` and `#journey` IDs so the navbar continues to scroll to each section.
- Use semantic section headings with `aria-labelledby` relationships.
- Share one panel style for both sections.
- Keep the sections static and Django-rendered; no view, model, database, or JavaScript changes are needed.
- Use responsive spacing so the panels remain readable on narrow screens.

## Definition of done

- [x] Projects and Journey contain truthful coming-soon messages.
- [x] Both sections use the shared coming-soon panel style.
- [x] The existing navigation anchors remain functional.
- [x] Projects placeholder links to the database-backed Projects page.
- [x] Journey is a truthful placeholder without fabricated milestones.
- [ ] Desktop and mobile behavior are manually checked; live browser verification is pending.

## Verification log

Checked 2026-09-07:

- [x] Static audit confirms both truthful placeholder messages and the expected section order.
- [x] Live desktop/mobile behavior remains unverified because no browser target is available.
