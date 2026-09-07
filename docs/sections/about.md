# About Section Sub-plan

Status: Implemented; live browser verification pending

Parent plan: [Portfolio layout plan](../portfolio-layout-plan.md)

## Purpose

Create the About section as a concise first-person narrative that explains Victoriano's story, values, and current direction without repeating the Profile section.

The section should help recruiters and academic evaluators understand the person behind the portfolio, while remaining useful to collaborators and friends.

## Agreed direction

- Write in English.
- Use a professional tone with a personal voice.
- Keep the narrative between 150 and 220 words.
- Center the story on the National Olympiad in Informatics as a turning point.
- Show how consistent effort and discipline developed problem-solving ability.
- Include teaching and mentorship as meaningful parts of Victoriano's growth.
- Describe the current direction as exploring software, technology, and meaningful impact.
- Mention current Computer Science study at Universitas Indonesia and faculty scholarship support.
- Do not mention Monash University.
- Do not mention discrimination or financial hardship.
- Do not repeat the Profile's exact identity facts, silver-medal statement, or social links.
- Do not list every job or organization; reserve detailed experience history for the future Journey sub-plan.
- Do not add a dedicated call-to-action to this section.

## Content structure

### Narrative

Use this progression:

1. The National Olympiad in Informatics became a major turning point.
2. Consistent effort, discipline, and trying different possibilities developed problem-solving ability.
3. Teaching and mentorship became important parts of personal and professional growth.
4. Current exploration focuses on software, technology, and meaningful impact.

### Focus panel

Use the heading `Focus` and show three compact items:

- **Problem-solving** — approaching difficult questions with patience, discipline, and persistence.
- **Teaching & mentorship** — sharing knowledge and helping others build confidence and capability.
- **Software, technology & impact** — exploring how technical work can contribute to people and communities.

## Proposed draft copy

> Discovering the National Olympiad in Informatics became a turning point in my development. I entered a demanding problem-solving environment without knowing exactly how far I could go, and the experience taught me that progress depends on consistent effort, discipline, and the willingness to try different possibilities. More than an achievement, NOI changed the way I approach difficult problems: I learn from setbacks, stay patient, and keep working until I find a clearer path forward.
>
> I am now studying Computer Science at Universitas Indonesia with support from a faculty scholarship. Alongside my studies, I continue exploring software and technology while teaching and mentoring students in competitive programming. These experiences have shown me that learning becomes more meaningful when it is shared. Helping someone understand a difficult concept, improve their problem-solving process, or gain confidence has become an important part of my growth.
>
> At this stage, I am still exploring the possibilities of what I can build and contribute through technology. My direction is shaped by curiosity, continuous learning, persistence, and a desire to create meaningful impact. I want to keep strengthening my technical foundation, learning from different experiences, and finding ways to use technology in service of people and communities.

## Implementation plan

### Template

- Replace the empty `<section id="about" class="about-section"></section>` with semantic section content.
- Keep the existing `id="about"` anchor so the navbar continues to work.
- Use a heading hierarchy below the Profile `h1`, with an About `h2` and a heading for the Focus panel.
- Use an `aside` or equivalent supporting-content landmark for the Focus panel.
- Keep the section static; no view, model, database, or JavaScript changes are needed.

### Styles

- Reuse the shared `.content-section` and `.section-grid` styles from the master plan.
- Use a two-column layout on desktop: narrative on the left and Focus panel on the right.
- Stack the columns on mobile.
- Preserve the warm cream, brown, purple, and pink visual identity.
- Keep spacing consistent with the Profile and future sections.
- Ensure the fixed navbar does not cover the `#about` heading when navigating to the anchor.

### Accessibility

- Use semantic headings and readable paragraph structure.
- Keep the Focus items as a list rather than styling plain text as a list.
- Preserve visible focus states for any future links.
- Verify readable contrast for the narrative, panel, labels, and section background.
- Do not make meaning depend on color, animation, or hover behavior.

## Definition of done

- [x] The approved draft or an explicitly revised version is present in the template.
- [x] The About section uses the agreed first-person English voice and stays within 150–220 words. The current template narrative is 90 words (static audit, 2026-09-07).
- [x] The section does not duplicate Profile facts or detailed Journey entries.
- [x] The Focus panel contains the three agreed items.
- [x] The desktop layout uses narrative-left and Focus-right columns.
- [x] The mobile layout stacks the content cleanly.
- [x] The `#about` navbar link lands below the fixed navbar.
- [x] The section uses semantic markup.
- [x] Readable contrast has been visually verified.
- [x] Desktop and mobile behavior are manually checked.

## Verification log

Checked 2026-09-07:

- [x] Static markup and Focus-panel structure verified.
- [x] Live desktop/mobile behavior and contrast remain unverified because no browser target is available.
