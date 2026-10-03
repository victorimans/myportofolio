# Portfolio Site Context

This context defines the vocabulary for the personal portfolio and the information it presents.

## Language

**Profile**:
The primary landing section presenting Victoriano's identity, photo, biography, academic details, and social links.
_Avoid_: Hero, Home (when referring to the content section)

**About**:
The first-person narrative section explaining Victoriano's story, motivations, personal values, and current direction for recruiters, academic evaluators, collaborators, and friends.
Its story centers on the National Olympiad in Informatics as a turning point, the effort required to develop problem-solving ability, and the continuing roles of teaching and mentorship.
Its current direction is to explore software, technology, and meaningful impact while studying Computer Science at Universitas Indonesia with faculty scholarship support.
It emphasizes hard work, discipline, continuous learning, curiosity, persistence, and exploring possibilities without discussing private hardship or discrimination.
The About section complements the Profile and should not repeat its identity, photo, academic quick facts, or social links.

**Skills**:
The section describing Victoriano's demonstrated capabilities and relevant technologies, organized into Problem-solving & competitive programming, Teaching & mentorship, and Software development & technology.
It should use grouped skills with short context, without self-rated proficiency levels, and should not repeat the About narrative or detailed achievements reserved for Journey.
_Avoid_: Skill bars, arbitrary proficiency ratings, biography, detailed journey milestones

**Projects**:
The database-backed collection of Victoriano's software and technology work at `/projects/`, distinct from the coming-soon Projects section on the landing page. The listing is loaded from the public JSON endpoint, supports title search with a 300 ms debounce, and offers project detail pages. The portfolio owner (superuser) can create projects through an AJAX modal and remove them; Editors can update project content; authenticated users can toggle a star. Project input is stripped of HTML tags by form validation, and dynamic cards are constructed with text-safe DOM APIs.
_Avoid_: Placeholder project cards, fabricated project details, treating star membership as project content

**Project owner**:
The portfolio-maintainer role with full authority over Project records, including creating, changing, and removing them, as well as reading and expressing appreciation for them.
_Avoid_: Confusing ownership of the portfolio with ownership of an individual star

**Editor**:
A registered account assigned membership in the exact Django group named `Editor` by an administrator. An Editor may read and update Project and Blog post content, but may not create or remove those records through the public portfolio workflows.
_Avoid_: Treating editor status as permission to change star membership or manage accounts

**Star**:
An authenticated user's reversible expression of appreciation for one Project or Blog post. A user may have at most one active star for a given record; public pages may show the total count and whether the current user has starred it, while public JSON does not expose individual star membership or account identities.
_Avoid_: Publicly identifying the users who starred a Project or Blog post

**Journey**:
The portfolio section for Victoriano's academic, competition, mentorship, and professional milestones, presented when those milestones are ready to publish.
_Avoid_: Repeating the About narrative, unsupported achievements

**Contact**:
The final portfolio section inviting relevant professional or academic conversations with Victoriano.
_Avoid_: Contact form, response-time promises, unsupported availability claims

**Blog**:
The public portfolio area for Victoriano's personal and technical writing, kept separate from Projects and Journey. Blog posts are readable by visitors; superusers create or remove them, Editors update them, and authenticated users may express appreciation with a star.
_Avoid_: Treating Blog as a project showcase, an academic milestone list, or static portfolio content

**Blog post**:
An individual written piece presented publicly in the Blog area, with its own title, body, category, optional picture link, and creation date. Authenticated users can toggle a star; the public presentation may show the total count and the current user's own state without identifying other users. There is no draft visibility in the current domain.
_Avoid_: Article when referring to the portfolio's canonical content type

**Blog search**:
The Assignment 5 target for visitor-facing search over public Blog post titles. It matches partial titles without regard to letter case and does not require a full-page reload; this glossary entry describes the agreed target, not a claim that it is already implemented.
_Avoid_: Treating search as a filter over private or unpublished posts

**Blog editor**:
A registered user who belongs to the exact `Editor` group and may update Blog post content. Editor membership alone does not grant permission to create or delete posts.
_Avoid_: Assuming registration grants Editor membership

**Coming-soon placeholder**:
A truthful temporary section message indicating that Projects or Journey content is intentionally not yet published.
_Avoid_: Fake records, inactive interactions

**Static portfolio content**:
The fixed Profile, About, Skills, landing-page Projects/Journey placeholders, and Contact content presented on the landing page. Database-backed Projects, Experience, and Blog records are separate dynamic content.
_Avoid_: Treating database content as static landing-page content

**Experience**:
A database-backed work, research, internship, volunteer, part-time, full-time, or freelance record displayed on `/experience/`. Its ongoing status is derived from whether an end date is absent. It is separate from the static landing-page Journey placeholder; no public Experience create/update/delete workflow is currently defined.
_Avoid_: Treating Experience as the Journey section or assuming public CRUD exists

**Project search**:
The title search on `/projects/`, backed by `/api/projects/`. Input changes are debounced by 300 ms, in-flight fetches can be aborted, and the browser URL is updated without a full-page navigation.
_Avoid_: Assuming search is server-rendered as a full-page form submission

**Project modal**:
The superuser-only popover form used to add a Project from the Projects listing. Submission uses AJAX to `/projects/add-ajax/`; successful creation closes/resets the form, displays a toast, and refreshes the current listing.
_Avoid_: Confusing the modal with the separate traditional `/projects/add/` form route

**Mahasiswa**:
A classroom hands-on record containing a student's name and NPM, displayed in the separate Mahasiswa section and managed through the Django admin.
_Avoid_: Treating classroom Mahasiswa records as static portfolio content or portfolio milestones
