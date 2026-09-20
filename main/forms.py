from django import forms
from django.forms import ModelForm, TextInput, Textarea, URLInput

from main.models import BlogPost, Project


class ProjectForm(ModelForm):
    secret = forms.CharField(
        label="Kode Rahasia",
        required=False,
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Masukkan kode rahasia",
                "autocomplete": "current-password",
            }
        ),
    )

    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
        ]
        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "tech_stack": "Teknologi yang Digunakan",
            "project_url": "URL Proyek",
            "project_image_url": "URL Gambar Proyek",
        }
        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Proyekmu",
                    "rows": 3,
                }
            ),
            "tech_stack": TextInput(
                attrs={
                    "placeholder": "Django, Python, HTML, CSS",
                }
            ),
            "project_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/kakBurhan/burhanquestv4",
                }
            ),
            "project_image_url": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
        }


class BlogPostForm(ModelForm):
    class Meta:
        model = BlogPost
        fields = ["title", "content", "category", "picture_link"]
        labels = {
            "title": "Judul Blog",
            "content": "Isi Blog",
            "category": "Kategori Blog",
            "picture_link": "Link Gambar",
        }
        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Judul tulisan",
                    "maxlength": 255,
                }
            ),
            "content": Textarea(
                attrs={
                    "placeholder": "Tulis isi blogmu",
                    "rows": 8,
                }
            ),
            "category": forms.Select(
                attrs={
                    "placeholder": "AI, DSA, Web Development",
                }
            ),
            "picture_link": URLInput(
                attrs={
                    "placeholder": "https://example.com/gambar-blog.jpg",
                }
            ),
        }
