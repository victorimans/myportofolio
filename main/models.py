import uuid
from django.db import models

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    tech_stack = models.CharField(max_length=255)
    project_url = models.URLField(blank=True)
    project_image_url = models.URLField(blank=True, max_length=500)

    def __str__(self):
        return self.title


class Mahasiswa(models.Model):
    nama = models.CharField(max_length=30)
    npm = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.nama} ({self.npm})"


class BlogPost(models.Model):
    BLOG_CATEGORY_CHOICES = [
        ("ai", "AI"),
        ("dsa", "DSA"),
        ("web-development", "Web Development"),
        ("career", "Career"),
        ("personal", "Personal"),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(
        max_length=30,
        choices=BLOG_CATEGORY_CHOICES,
        default="ai",
    )
    picture_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
