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
The portfolio section and collection of Victoriano's software and technology work. A Project is a published work record with descriptive content and optional external links or imagery; visitors can read it, while account roles govern who may change it and authenticated users may express appreciation with a star.
_Avoid_: Placeholder project cards, fabricated project details, treating star membership as project content

**Project owner**:
The portfolio-maintainer role with full authority over Project records, including creating, changing, and removing them, as well as reading and expressing appreciation for them.
_Avoid_: Confusing ownership of the portfolio with ownership of an individual star

**Editor**:
A registered account assigned the Editor role by the portfolio administrator. An Editor may read and change Project content, but may not create or remove Projects.
_Avoid_: Treating editor status as permission to change star membership or manage accounts

**Star**:
An authenticated user's reversible expression of appreciation for one Project. A user may have at most one active star for a given Project; the public presentation may show the total count and whether the current user has starred it.
_Avoid_: Publicly identifying the users who starred a Project

**Journey**:
The portfolio section for Victoriano's academic, competition, mentorship, and professional milestones, presented when those milestones are ready to publish.
_Avoid_: Repeating the About narrative, unsupported achievements

**Contact**:
The final portfolio section inviting relevant professional or academic conversations with Victoriano.
_Avoid_: Contact form, response-time promises, unsupported availability claims

**Blog**:
The portfolio area for Victoriano's personal and technical writing, kept separate from Projects and Journey.
_Avoid_: Treating Blog as a project showcase, an academic milestone list, or static portfolio content

**Blog post**:
An individual written piece presented in the Blog area, with its own title, body, and creation date.
_Avoid_: Article when referring to the portfolio's canonical content type

**Coming-soon placeholder**:
A truthful temporary section message indicating that Projects or Journey content is intentionally not yet published.
_Avoid_: Fake records, inactive interactions

**Static portfolio content**:
The fixed personal, academic, skills, project, journey, and contact information presented as part of the portfolio.
_Avoid_: Database content, dynamic portfolio records

**Mahasiswa**:
A classroom hands-on record containing a student's name and NPM, displayed in the separate Mahasiswa section and managed through the Django admin.
_Avoid_: Treating classroom Mahasiswa records as static portfolio content or portfolio milestones
