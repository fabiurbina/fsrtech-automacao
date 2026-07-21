from django.urls import path
from .views import home, login_view, logout_view, viesano_insights    
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path(
        "alterar-senha/",
        auth_views.PasswordChangeView.as_view(
            template_name="alterar_senha.html"
        ),
        name="password_change",
    ),

    path(
        "alterar-senha/concluido/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="alterar_senha_sucesso.html"
        ),
        name="password_change_done",
    ),
    
    path(
    "insights/<int:numero_pedido>/",
    viesano_insights,
    name="viesano_insights",
),

    
]