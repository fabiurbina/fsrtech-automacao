from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def criacao_de_sites(request):
    return render(request, 'criacao_de_sites.html')