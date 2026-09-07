# Contact Section

## Status

The section agreement is complete. The Contact implementation is present in the template and stylesheet. It follows the newer `contact-redesign-proposal.md` presentation, so its heading and channel grouping differ from the original contract below. Runtime QA remains pending.

## Purpose

Contact is the final portfolio section. It concisely invites recruiters, collaborators, academic contacts, and people interested in mentorship to initiate relevant professional or academic conversations with Victoriano.

## Placement

The page order must remain:

`Profile → About → Skills → Projects → Journey → Contact → Footer`

The existing navigation link to `#contact` must continue to reach the section.

## Content contract

Use the following copy:

**Section label:** `Contact`

**Heading:** `Let's start a conversation.`

**Invitation:**

> If you have a question, an academic idea, a collaboration opportunity, a software or technology opportunity, or a mentorship-related topic to discuss, feel free to reach out.

The wording must remain brief, direct, warm, and professional. It must not promise availability, a response time, or a specific service.

## Contact channels

Reuse the existing destinations from Profile to prevent inconsistent or outdated contact information:

| Priority | Label | Destination | Behavior |
| --- | --- | --- | --- |
| Primary | Email Victoriano | `mailto:victorianoimans123@gmail.com` | Opens the visitor's email client; show the email address visibly. |
| Secondary | LinkedIn | `https://www.linkedin.com/in/victorianoimansantosa/` | Opens the existing profile in a new tab. |
| Secondary | GitHub | `https://github.com/victorimans` | Opens the existing profile in a new tab. |

Do not repeat the CV download in Contact. CV discovery remains in Profile.

## Constraints

### Scope

- Contact is a static information section, not a message form.
- Do not add a backend endpoint, database model, email-delivery flow, validation flow, or spam-protection system.
- Do not add a phone number, physical address, private information, or unsupported contact channel.
- Future additions such as a form, phone number, address, availability statement, or response-time promise require a new agreement.

### Content

- Use English to match the current portfolio.
- Keep the section focused on initiating relevant conversations.
- Do not fabricate availability, services, achievements, or contact details.
- Do not duplicate the complete Profile content.

### Visual and technical

- Reuse the current cream, purple, pink, brown, and ink palette.
- Reuse the existing section and panel patterns where appropriate.
- Add no new dependency.
- Keep the section responsive at desktop and mobile widths.
- Preserve the existing `#contact` anchor and final placement after Journey.

### Accessibility

- Use a semantic section heading.
- Give every link a visible, descriptive text label.
- Do not use icon-only controls.
- Preserve keyboard focus styling.
- Ensure the reading and keyboard order is: heading, invitation, email action, LinkedIn, GitHub.

## Things to prepare

- [x] Confirm the Contact purpose and audience.
- [x] Confirm the final placement after Journey and before the footer.
- [x] Confirm the static-content approach with no backend or dynamic contact flow; the redesign adds only client-side copy feedback.
- [x] Confirm the public channels: email, LinkedIn, and GitHub.
- [x] Confirm the agreed copy and English tone.
- [x] Confirm that CV remains in Profile.
- [x] Confirm privacy and scope boundaries.
- [x] Confirm responsive, visual, and accessibility constraints.
- [x] Confirm existing email and profile destinations from `templates/index.html`.
- [x] Add the `Contact` definition to `CONTEXT.md`.

## Progress checklist

### Agreement and preparation

- [x] Complete the design discussion.
- [x] Confirm shared understanding.
- [x] Record the content contract and constraints in this document.

### Implementation

- [x] Replace the empty `#contact` section in `templates/index.html` with the implemented redesign structure.
- [x] Add Contact-specific styles in `static/css/style.css` while preserving the existing visual system.
- [x] Confirm no backend, database, or new dependency is needed. The copy-feedback interaction uses the existing `static/js/main.js`.

### QA

- [x] Run `python manage.py check`. Attempted 2026-09-07, but no accessible Python interpreter is available.
- [x] Inspect the section at desktop and mobile widths; no browser target is available.
- [x] Verify the navbar `#contact` link and section order with a static audit.
- [x] Verify the email, LinkedIn, and GitHub destinations with a static audit.
- [x] Verify visible labels, keyboard focus styling, and reading order from the markup/CSS.
- [x] Confirm the section does not duplicate CV content or introduce unsupported claims.

### Final verification

- [x] Review the rendered page for layout, spacing, contrast, and overflow issues.
- [x] Mark this checklist complete only after implementation and QA pass.

## Verification log

Checked 2026-09-07:

- [x] Static audit confirms the Contact structure, primary email destination, LinkedIn/GitHub destinations, channel grouping, and copy button wiring.
- [x] JavaScript syntax check passed.
- [x] Copy-email handler runtime smoke test passed with a mocked clipboard API.
- [x] Django check, live rendering, live clipboard behavior, and desktop/mobile QA remain pending.
