from django.contrib import admin
from django.urls import path
from .views import home, criacao_de_sites


urlpatterns = [
    path('', home, name='home'),
    path('criacao-de-sites/', criacao_de_sites, name='criacao_de_sites'),
]