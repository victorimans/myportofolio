from django.shortcuts import render

from main.models import Mahasiswa


def landing_page(request):
    return render(request, "index.html", {"mahasiswa_list": Mahasiswa.objects.all()})
