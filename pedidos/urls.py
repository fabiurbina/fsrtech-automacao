from django.contrib import admin
from django.urls import path
from .views import home, criacao_de_sites, orcamento_facil

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('criacao-de-sites/', criacao_de_sites, name='criacao_de_sites'),
    path('orcamento-facil/', orcamento_facil, name='orcamento_facil'),
]
