# Portfolio Layout Plan

Status: In progress — profile, body sections, footer, and Contact implementation are present; visual and Django verification remain; Blog checkpoint is documented and implementation is pending

## Sub-plan index

- [x] [About section sub-plan](sections/about.md) created and aligned with the agreed direction.
- [x] [Skills section sub-plan](sections/skills.md) created and aligned with the agreed direction.
- [x] [Blog section sub-plan](sections/blog.md) created and aligned with the agreed direction; implementation remains pending.
- [x] Create the Projects, Journey, and Contact sub-plans when those focused sessions begin.

## Progress check

Last checked: 2026-09-12

### Done

- [x] Profile uses `#profile` and `.profile-section`.
- [x] Related profile classes use the `profile-*` naming.
- [x] The brand link points to `#profile`.
- [x] The profile has a two-column desktop layout and stacks on mobile.
- [x] The cream, brown, purple, and pink visual identity is preserved.
- [x] The Bootstrap navbar and falling sakura effect are preserved.
- [x] The profile content and GitHub, LinkedIn, and email links are present.
- [x] The profile includes a `Download CV` link to the shared Google Drive PDF, opening in a new tab.
- [x] The page remains a single Django-rendered page with static content; no view, settings, model, migration, or dependency changes are needed.
- [x] The section anchors for About, Skills, Projects, Journey, and Contact are present.
- [x] The page uses a full-height flex layout so the footer can stay at the bottom of short pages.
- [x] The footer aligns its three items in a row on desktop and stacks them on mobile.
- [x] The footer includes a Back to top link pointing to `#profile`.
- [x] The unused AOS stylesheet, script, and `AOS.init()` call have been removed.
- [x] Reduced-motion handling is present for smooth scrolling, transitions, and sakura animation.
- [x] Visible focus styles are present for links and buttons.
- [x] The Blog scope, naming, content contract, and implementation checklist are documented in the [Blog sub-plan](sections/blog.md).

### Not yet done

- [x] Implement the About section using the [About sub-plan](sections/about.md); live browser verification remains pending.
- [x] Add the Skills, Projects, Journey placeholder, and Contact content/layout.
- [x] Add shared `.content-section`, `.section-grid`, heading, label, and supporting-copy styles.
- [x] Add the responsive skills list.
- [ ] Add project cards; Projects intentionally remains a truthful coming-soon placeholder.
- [x] Finish the Contact call-to-action area using the Contact redesign proposal.
- [ ] Verify readable contrast across the current palette and the completed sections.
- [ ] Add the future top-navigation `Download CV` item after the About work is complete and the CV PDF exists.
- [ ] Run Django checks and browser verification. Attempted on 2026-09-07, but `env\Scripts\python.exe` resolves to an inaccessible Python installation, the system Python launcher is unavailable, and no browser target is exposed for live verification.
- [ ] Implement the database-backed Blog section according to the [Blog sub-plan](sections/blog.md), then run its migration, tests, and server verification.

## Follow-up session breakdown

Complete the remaining work as focused sessions. Each session should update the checklist above and verify its own responsive behavior before moving on.

1. **Shared section foundation** — implemented; desktop/mobile visual verification remains pending.
   - Add the reusable section container, grid, heading, label, supporting-copy, and alternating-background styles.
   - Confirm the shared styles work at desktop and mobile widths.

2. **About section** — implemented, but the current narrative is 90 words and still needs to meet the 150–220 word requirement; browser verification remains pending.
   - Follow the [About sub-plan](sections/about.md) for the approved copy, Focus panel, layout, and acceptance criteria.
   - Add the About copy and supporting details.
   - Use the shared section structure and confirm the `#about` anchor lands below the fixed navbar.

3. **Skills section** — implemented; browser verification remains pending.
   - Follow the [Skills sub-plan](sections/skills.md) for the agreed categories, content, and acceptance criteria.
   - Add the skills content and responsive skills list.
   - Check wrapping, spacing, and readability on narrow screens.

4. **Projects section** — intentionally kept as a coming-soon placeholder; project cards remain deferred.
   - Add the project cards and their links/content.
   - Confirm the three-column desktop layout collapses to one column on mobile.

5. **Journey section** — intentionally kept as a coming-soon placeholder.
   - Add the academic, olympiad, coaching, and other journey milestones.
   - Keep the markup readable and verify the section spacing against the neighboring sections.

6. **Contact section** — implemented from the redesign proposal; browser and clipboard verification remain pending.
   - Add the contact call-to-action and reuse the existing email/social destinations where appropriate.
   - Confirm the CTA is clear, keyboard reachable, and readable in both themes/backgrounds.

7. **Accessibility and visual polish** — static structure and reduced-motion/focus rules are present; contrast and live responsive verification remain pending.
   - Verify semantic structure, focus states, image text, contrast, reduced motion, and fixed-navbar anchor behavior across all sections.

8. **Final verification** — blocked by unavailable Python/browser tooling.
   - Run Django checks once Python/Django access is available.
   - Verify desktop/mobile rendering, collapsed navigation, all anchors and external links, footer behavior, and browser-console errors.

9. **Blog section** — documentation checkpoint complete; implementation pending.
   - Add the `BlogPost` model, migration, Admin registration, `/blog/` route/view/template, navbar links, minimal styles, and required tests.
   - Follow the [Blog sub-plan](sections/blog.md) and update its checklist and verification log after implementation.

## Deferred navigation item

- Add a `Download CV` item to the top navbar after the About section is complete and the CV PDF has been created. The item must work on desktop and collapsed mobile navigation and point to the tested CV file.

## Goal

Refine the existing warm editorial portfolio so the profile and body sections have a complete responsive layout, while making the footer behave correctly on desktop and mobile.

## Agreed direction

- Keep the cream, brown, purple, and pink visual identity. 
- Keep the existing Profile, About, Skills, Projects, Journey, and Contact sections.
- Keep the existing profile content and external links.
- Keep the Bootstrap navbar and falling sakura effect.
- Keep the existing landing page as one Django-rendered page with static portfolio content. The dedicated Blog page is an approved dynamic exception backed by `BlogPost` records.
- Preserve useful code comments and update comments that describe removed or renamed markup.

## Layout changes

### Profile

- Rename the first section from `#home` / `.hero-section` to `#profile` / `.profile-section`.
- Rename related `hero-*` classes to `profile-*` where they describe the profile section.
- Point the brand and Back to top links to `#profile`.
- Keep a two-column desktop layout with identity/details and photo, then stack them on mobile.

### Body

- Add the missing shared section layout rules for `.content-section`, `.section-grid`, headings, labels, and supporting copy.
- Use consistent vertical spacing and the existing alternating tinted sections.
- Use a responsive skills list.
- Display projects as three cards on desktop and one column on mobile.
- Keep the contact section as a clear call-to-action area.
- Preserve the current container-based structure and avoid adding unnecessary JavaScript.

### Footer

- Make the page a full-height flex layout so the footer stays at the bottom when content is short.
- Align copyright, university affiliation, and Back to top in one row on desktop.
- Stack those three items cleanly on mobile.

### JavaScript and accessibility

- Remove the unused `AOS.init()` call because AOS is not loaded and no AOS animations are used.
- Keep the sakura effect.
- Respect `prefers-reduced-motion` for smooth scrolling and sakura animation.
- Preserve semantic markup, visible focus states, descriptive image text, and readable contrast.

## Files in scope

- `templates/index.html`: profile naming, anchors, and comments only; preserve content.
- `static/css/style.css`: complete body/profile/footer layout, responsive rules, and reduced-motion handling.
- `static/js/main.js`: remove the broken AOS initialization and keep the sakura behavior.

## Files intentionally out of scope for the layout work

- `portofolio/views.py`: no view change is needed.
- `portofolio/settings.py`: no Django configuration change is needed.
- Database models, migrations, admin content, and new frontend dependencies.

These exclusions apply to the layout work described above. They do not apply to the separately scoped Blog implementation, which is defined in the [Blog sub-plan](sections/blog.md).

## Verification after approval

- Run Django’s project checks.
- Confirm the page renders through the Django route.
- Check desktop and mobile widths, including the collapsed navbar.
- Check that the footer aligns correctly, stacks on mobile, and reaches the bottom of short pages.
- Check Profile, navigation, Back to top, email, GitHub, and LinkedIn links.
- Check the browser console for JavaScript errors.

## Verification log

Checked 2026-09-07:

- [x] Static structural audit: section order, anchors, Skills, Projects/Journey placeholders, Contact links, footer, reduced motion, and absence of AOS usage.
- [x] JavaScript syntax check passed.
- [x] Copy-email handler runtime smoke test passed with a mocked clipboard API.
- [x] Tracked HTML element opening/closing tag counts match.
- [x] Django check: blocked because no accessible Python interpreter is available.
- [x] Live desktop/mobile browser verification: blocked because no browser target is available in the current environment.
- [x] About narrative requirement: not met; the current narrative is 90 words, below the required 150–220 words.
