from django.core.management.base import BaseCommand
from django.utils import timezone

from main.models import Experience


EXPERIENCES = [
    {
        "title": "Teaching Assistant — Discrete Mathematics 1 (Faculty of Computer Science, Universitas Indonesia)",
        "description": (
            "Teaching Assistant for Discrete Mathematics 1 at the Faculty of Computer Science, "
            "Universitas Indonesia."
        ),
        "category": "part-time",
        "ongoing": True,
    },
    {
        "title": "Software Engineer — KMK Fasilkom UI",
        "description": (
            "Contributed as a software engineer for KMK Fasilkom UI by helping develop and "
            "maintain the organization’s website and digital platform."
        ),
        "category": "freelance",
        "ongoing": True,
    },
    {
        "title": "Relationship Officer — KMK Fasilkom UI",
        "description": (
            "Served as a Relationship Officer by helping maintain communication with members, "
            "alumni, and related people of KMK Fasilkom UI. Assisted in coordinating outreach "
            "and communication for organizational activities, including preparations for the "
            "Weekend event, which aims to strengthen connection, solidarity, and engagement "
            "between KMK Fasilkom UI members and alumni. Supported event coordination, "
            "follow-ups, and communication to ensure the activity runs effectively."
        ),
        "category": "volunteer",
        "ongoing": True,
    },
    {
        "title": "Competitive Programming Tutor — Kokocoder Group",
        "description": (
            "Guided and assisted students in learning competitive programming concepts, "
            "problem-solving strategies, and algorithmic thinking. Helped students understand "
            "how to approach programming problems more systematically and efficiently. "
            "Supported their learning process by explaining solution ideas, discussing problem "
            "patterns, and helping them improve their coding logic and speed."
        ),
        "category": "part-time",
        "ongoing": True,
    },
    {
        "title": "Vice Manager — Knight Camp (Kokocoder Group)",
        "description": "Served as Vice Manager for Knight Camp under Kokocoder Group.",
        "category": "volunteer",
        "ongoing": False,
    },
    {
        "title": "Software Engineer — Knight Camp 9.0 (Kokocoder Group)",
        "description": (
            "Contributed as a software engineer by studying and reviewing codebases, "
            "understanding code walkthroughs, and learning how existing systems are structured "
            "and implemented. Gained practical experience in setting up projects locally, "
            "running applications in a local development environment, and performing testing "
            "to ensure the program works as expected. This role helped strengthen my "
            "understanding of real-world development workflows, debugging, testing, and code "
            "comprehension."
        ),
        "category": "freelance",
        "ongoing": False,
    },
    {
        "title": "Human Resources Officer — COMPFEST",
        "description": (
            "Supported recruitment processes, including interview scheduling, candidate "
            "coordination, and applicant communication. Coordinated with internal teams to "
            "help ensure a smooth selection and onboarding process. Assisted with administrative "
            "HR tasks, follow-ups, and team communication."
        ),
        "category": "freelance",
        "ongoing": True,
    },
    {
        "title": "Office Associate — Azer Technologies Inc.",
        "description": (
            "Supported the early development of Azer Technologies Inc., a company initiated "
            "from a side project built together with friends. Assisted team members with "
            "operational, administrative, and coordination-related tasks to help the project "
            "run more smoothly. Contributed to internal communication, task organization, and "
            "general support needed during the early stages of building and developing the "
            "initiative."
        ),
        "category": "freelance",
        "ongoing": True,
    },
    {
        "title": "Member — Google Developer Groups on Campus Universitas Indonesia (GDGoC UI)",
        "description": (
            "Participated as a member of Google Developer Groups on Campus Universitas "
            "Indonesia by engaging in technology-related activities, discussions, and "
            "community events. Gained exposure to developer communities, technical learning "
            "opportunities, and collaborative projects related to software development, "
            "technology, and innovation."
        ),
        "category": "volunteer",
        "ongoing": False,
    },
    {
        "title": "Public Relations Officer — Sospro PMB Fasilkom Universitas Indonesia",
        "description": (
            "Actively contributed as a Public Relations Officer by participating in group "
            "discussions, sharing ideas, and supporting communication-related activities. "
            "Helped provide input for planning and outreach strategies, contributed to "
            "brainstorming sessions, and assisted the team in maintaining active coordination. "
            "This role developed communication, teamwork, and idea-generation skills within "
            "an organizational setting."
        ),
        "category": "part-time",
        "ongoing": False,
    },
]


class Command(BaseCommand):
    help = "Seed the portfolio Experience records. Safe to run more than once."

    def handle(self, *args, **options):
        for experience_data in EXPERIENCES:
            data = experience_data.copy()
            ongoing = data.pop("ongoing")
            defaults = {
                **data,
                "ended_at": None if ongoing else timezone.now(),
            }
            _, created = Experience.objects.update_or_create(
                title=data["title"],
                defaults=defaults,
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action}: {data['title']}")

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(EXPERIENCES)} experiences."))
