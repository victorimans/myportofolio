from django.contrib import admin
from .models import BlogPost, Experience, Mahasiswa

admin.site.register(Mahasiswa)
admin.site.register(Experience)
admin.site.register(BlogPost)
