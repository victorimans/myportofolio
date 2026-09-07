# Contact Redesign Proposal

**Status:** Implemented in the current template; live browser and clipboard verification pending  
**Scope:** Contact section only  
**Implementation:** Present in `templates/index.html`, `static/css/style.css`, and `static/js/main.js`. The repository does not record formal approval of this proposal, so review remains an outstanding documentation item.

The current implementation uses the recommended options from Round 2, but implementation should not be treated as proof that the proposal was formally approved.

## 1. Problem

The current Contact section is a single centered panel containing:

- a generic `Contact with Email` button;
- a paragraph of invitation text; and
- a flat row of social links.

The result is clear, but visually monotonic. The email action, professional profiles, competitive-programming profiles, and personal profile all receive almost the same visual treatment. The section does not yet communicate much about Victoriano's identity as a student, mentor, and software-oriented creator.

## 2. Agreed direction

The redesign should be:

- a warm personal invitation with one obvious next action;
- an editorial correspondence card that fits the existing cream, brown, pink, and sakura visual language;
- a small amount of interaction—hover states, channel-card motion, and copy feedback—without becoming a gimmick;
- explicit about the email address;
- organized by the purpose of each contact channel; and
- free of a contact form, response-time promise, or unsupported availability claim.

## 3. Proposed experience

### Concept: an editorial conversation card

Replace the single centered text block with a structured card that feels like a personal letter or correspondence desk:

```text
┌─────────────────────────────────────────────────────────────┐
│ CONTACT                                      ✦               │
│                                                             │
│ Have an idea worth exploring?       ┌─────────────────────┐ │
│                                     │ START WITH EMAIL    │ │
│ A short personal invitation         │                     │ │
│ about academic ideas, software,     │ victorianoimans...  │ │
│ collaboration, or mentorship.       │ [Email me] [Copy]   │ │
│                                     └─────────────────────┘ │
│                                                             │
│ WE CAN TALK ABOUT                                           │
│ [Academic ideas] [Software & technology] [Collaboration]   │
│ [Mentorship]                                                │
│                                                             │
│ PROFESSIONAL        COMPETITIVE PROGRAMMING    PERSONAL     │
│ LinkedIn            Codeforces                  Instagram    │
│ GitHub              AtCoder                                  │
│                     TLX                                      │
└─────────────────────────────────────────────────────────────┘
```

On smaller screens, the content should stack in this order:

1. invitation and heading;
2. email card;
3. conversation-topic labels;
4. grouped channel cards.

This preserves the primary action and prevents the social links from becoming a dense horizontal line.

## 4. Content proposal

### Heading

Recommended draft:

> Have an idea worth exploring?

This is more personal and specific than `Let's start a conversation.` while remaining broad enough for academic, software, collaboration, and mentorship-related conversations.

### Invitation

Recommended draft:

> Whether you want to discuss an academic idea, software and technology, a collaboration, or mentorship, email is the best place to start.

This keeps the invitation grounded in the existing portfolio content. It does not promise availability or a response time.

### Primary email card

```text
START WITH EMAIL
victorianoimans123@gmail.com

[Email me]  [Copy email]
```

The visible address makes the destination transparent. `Email me` opens the existing `mailto:` action. `Copy email` copies the address and briefly changes its feedback to something such as `Copied`.

### Conversation topics

Use compact labels, not interactive filters:

- Academic ideas
- Software & technology
- Collaboration
- Mentorship

These labels are descriptive context. They should not imply a booking system or availability status.

### Channel groups

#### Professional

- LinkedIn
- GitHub

#### Competitive programming

- Codeforces
- AtCoder
- TLX

#### Personal

- Instagram

The professional group should have the strongest secondary emphasis. Competitive-programming profiles are useful evidence of Victoriano's technical identity, while Instagram should remain visible but visually quieter.

## 5. Visual behavior

### Hierarchy

1. Heading and invitation establish the human tone.
2. Email card is the dominant action.
3. Topic labels explain what kinds of conversation are relevant.
4. Channel groups provide supporting paths.

### Editorial details

- Keep the existing warm palette and sakura motif.
- Add a subtle inner rule, offset edge, or small decorative mark to suggest stationery/correspondence.
- Use icons only as supporting cues; the channel names must remain visible.
- Keep the card visually composed, with enough empty space around the email action.
- Avoid adding more falling petals inside the card; the existing background motion is already sufficient.

### Interaction

- Email and channel cards lift slightly on hover and focus.
- The email card gets the strongest hover treatment.
- `Copy email` provides immediate visible feedback and remains keyboard accessible.
- Respect `prefers-reduced-motion` already used by the site.

## 6. Accessibility and responsive requirements

- Keep a semantic `section` with `aria-labelledby`.
- Use real links for email and external profiles.
- Use a real button for `Copy email`, with an accessible label and status feedback.
- Do not rely on color alone to distinguish channel groups.
- Preserve visible keyboard focus styles.
- Keep the email address readable and wrap it safely on narrow screens.
- Ensure the grouped cards remain understandable when stacked on mobile.

## 7. Acceptance criteria for implementation

The implementation will be considered aligned with this proposal when:

- the email address is visible without hovering or clicking;
- `Email me` opens the existing email destination;
- `Copy email` works and communicates success;
- LinkedIn/GitHub, competitive-programming profiles, and Instagram are visually grouped by purpose;
- the contact section no longer presents every channel as one flat text row;
- the design still fits the existing portfolio visual language;
- the layout remains usable on mobile; and
- no contact form, response-time promise, or unsupported availability claim is introduced.

## 8. Round 2 — decisions for review

These decisions are intentionally left open until this draft is reviewed.

### Q1 — Heading copy

Should the heading use the recommended `Have an idea worth exploring?`, or should it keep the existing `Let's start a conversation.`?

**Recommendation:** `Have an idea worth exploring?` because it sounds more personal and gives the section a distinct voice.

### Q2 — Email card position

Should the email card sit beside the invitation on desktop, as shown in the wireframe, or below the invitation in a full-width row?

**Recommendation:** beside the invitation. It creates a stronger editorial composition and makes the primary action immediately scannable.

### Q3 — Topic labels

Should the four conversation topics be plain visual labels, or clickable links that prefill an email subject such as `Conversation about mentorship`?

**Recommendation:** plain visual labels for now. Prefilled subjects add behavior and maintenance without being necessary to make the section distinctive.

### Q4 — Channel card detail

Should each channel show only an icon and name, or also a short descriptor such as `Professional network`, `Code portfolio`, or `Personal updates`?

**Recommendation:** icon, name, and a very short descriptor on desktop; collapse to icon and name on mobile if space becomes tight.

### Q5 — Copy feedback wording

Which feedback should appear after copying the address?

- `Copied` — recommended; shortest and clearest.
- `Email copied` — more explicit but wider.

**Recommendation:** `Copied`.

## 9. Boundary of this draft

This proposal covers the presentation and interaction model of the Contact section. It does not change:

- the email address or external profile URLs;
- the rest of the portfolio content;
- the site's overall color palette or typography;
- the Contact glossary definition in `CONTEXT.md`; or
- any backend or database behavior.

## 10. Verification status

Checked 2026-09-07:

- [x] The email address is visible and the `Email me` action uses the existing `mailto:` destination.
- [x] `Copy email` is wired to the existing JavaScript copy-feedback behavior.
- [x] Copy-email handler runtime smoke test passed with a mocked clipboard API.
- [x] LinkedIn/GitHub, competitive-programming profiles, and Instagram are grouped by purpose.
- [x] The Contact section uses the existing visual language and does not add a form, response-time promise, or unsupported availability claim.
- [x] Desktop/mobile layout, keyboard interaction, live clipboard behavior, and rendered contrast are not yet live-verified.
- [x] Formal proposal approval is not recorded in the repository.
