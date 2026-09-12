# Skills Section Sub-plan

Status: Implemented; live desktop/mobile verification pending

Parent plan: [Portfolio layout plan](../portfolio-layout-plan.md)

## Purpose

Create a concise capability section that answers what Victoriano can do. The section should help recruiters, academic evaluators, and collaborators understand his practical strengths without repeating the About narrative or the detailed achievements reserved for Journey.

## Agreed direction

- Write in English.
- Use a professional, capability-focused tone.
- Organize the content into three categories:
  - Problem-solving & competitive programming
  - Teaching & mentorship
  - Software development & technology
- Start with two skills per category, for six skills total.
- Give every skill one short contextual sentence.
- Do not use self-rated proficiency levels, progress bars, percentages, or arbitrary rankings.
- Do not list specific programming languages or tools yet; add them only after they are confirmed.
- Keep the section static and Django-rendered; do not add database or admin-managed content.
- Do not add a narrative paragraph that repeats the About section.
- Do not add a dedicated call-to-action.
- Keep specific achievements, including the Asia Jakarta ICPC finalist result, for the future Journey sub-plan.

## Content structure

Use three responsive panels or cards. Each panel should contain a category heading, a short description, and a readable unordered list of skills.

### Problem-solving & competitive programming

- **Algorithmic problem-solving** — Breaking complex problems into structured, logical solutions.
- **Competitive programming** — Applying algorithms and problem-solving under contest constraints, including team settings.

### Teaching & mentorship

- **Clear technical explanation** — Explaining difficult concepts in a structured and understandable way.
- **Competitive programming coaching** — Guiding learners through practice, reasoning, and problem-solving.

### Software development & technology

- **Software development** — Building and improving software through practical projects.
- **Technology exploration** — Learning and evaluating technologies to discover useful ways to solve problems.

## Implementation plan

### Template

- Replace the empty `<section id="skills" class="skills-section"></section>` with semantic Skills content.
- Keep the existing `id="skills"` anchor so the navbar continues to work.
- Use a heading hierarchy below the Profile `h1`, with a Skills `h2` and category headings as `h3` elements.
- Represent each category as a semantic `article` or equivalent grouped content panel.
- Keep the skill items as unordered lists rather than styling plain text as a list.
- Keep the section static; no view, model, database, or JavaScript changes are needed.

### Styles

- Reuse the shared `.content-section` styles, existing spacing, typography, and visual identity.
- Display the three category panels in a row or balanced grid on desktop.
- Stack the panels into one column on mobile.
- Preserve readable wrapping, spacing, and contrast for the skill descriptions.
- Keep the fixed-navbar anchor behavior consistent with the About section.

### Accessibility

- Use semantic section, heading, panel, and list markup.
- Preserve a logical heading order and readable text sizing.
- Do not make meaning depend on color, animation, hover behavior, or proficiency indicators.
- Verify readable contrast for labels, headings, descriptions, panels, and section backgrounds.
- Ensure the responsive layout remains usable at narrow widths.

## Definition of done

- [x] The three categories and six initial skills are agreed.
- [x] The section uses grouped skills with short context and no proficiency ratings.
- [x] Specific languages, tools, and detailed achievements are intentionally deferred.
- [x] The empty `#skills` section is replaced with the agreed semantic content.
- [x] The desktop layout presents three balanced category panels.
- [x] The mobile layout stacks the panels cleanly.
- [x] The section uses semantic markup and accessible lists.
- [x] Readable contrast has been visually verified.
- [x] The `#skills` navbar link lands below the fixed navbar.
- [x] Desktop and mobile behavior are manually checked.

## Verification log

Checked 2026-09-07:

- [x] Static audit confirms three category panels and six skill items.
- [x] JavaScript syntax check and tracked HTML tag-balance smoke check passed.
- [x] Live desktop/mobile behavior remains unverified because no browser target is available.
