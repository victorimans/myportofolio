from django.contrib import admin
from .models import BlogPost, Experience, Mahasiswa, Project

admin.site.register(Mahasiswa)
admin.site.register(Experience)
admin.site.register(BlogPost)
admin.site.register(Project)
