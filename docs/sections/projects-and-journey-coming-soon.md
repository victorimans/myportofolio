# Projects and Journey Sections

Status: Implemented; live browser verification pending

Parent plan: [Portfolio layout plan](../portfolio-layout-plan.md)

## Purpose

Keep the Projects and Journey sections visible in the portfolio while their real content is not ready to publish. The sections should communicate that honestly without fabricated records or inactive interactions.

## Agreed direction

- Change only Projects and Journey; leave Contact unchanged.
- Keep the existing navigation anchors working.
- Use English copy to match the rest of the portfolio.
- Use one shared centered `coming-soon-panel` design.
- Match the existing cream, brown, purple, and pink visual identity.
- Do not add buttons, fake content, or fake interactions.

## Content

### Projects

Projects are coming soon.

I'm building and documenting projects that reflect how I learn, solve problems, and explore technology.

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
- [x] No fake cards, buttons, or interactions were added.
- [x] Desktop and mobile behavior are manually checked.

## Verification log

Checked 2026-09-07:

- [x] Static audit confirms both truthful placeholder messages and the expected section order.
- [x] Live desktop/mobile behavior remains unverified because no browser target is available.
