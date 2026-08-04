from django.shortcuts import render, redirect
from django.core.paginator import Paginator 
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from .mysql_service import (consultar_pedidos_cliente, 
                            consultar_todos_pedidos,
                            consultar_indicadores_producao, 
                            mrp)
from .status_service import interpretar_status
from .ia_service import gerar_resumo



@login_required
def home(request):

    cpf_cnpj = request.user.username

    numero_pedido = request.GET.get("pedido")
    titulo = request.GET.get("titulo", "").strip()

    email = request.user.email.lower()

    print("CPF logado:", cpf_cnpj)

    if "@viesano" in email:
        pedidos = consultar_todos_pedidos()
    else:
        pedidos = consultar_pedidos_cliente(cpf_cnpj)

    pedidos_cliente = []

    for pedido in pedidos:

        status = interpretar_status(
            pedido.get("descricao_etapa"),
            pedido.get("status_producao"),
            pedido.get("cenario_fiscal")
        )

        pedido["titulo"] = status["titulo"]
        pedido["descricao"] = status["descricao"]
        pedido["cor"] = status["cor"]

        pedidos_cliente.append(pedido)

    # Lista de status disponíveis para o filtro
    status_disponiveis = sorted(
        {pedido["titulo"] for pedido in pedidos_cliente}
    )

    # FILTRO POR NÚMERO DO PEDIDO
    if numero_pedido:
        pedidos_cliente = [
            pedido
            for pedido in pedidos_cliente
            if str(pedido["numero_pedido"]) == numero_pedido
        ]

    # FILTRO POR STATUS
    if titulo:
        pedidos_cliente = [
            pedido
            for pedido in pedidos_cliente
            if pedido["titulo"] == titulo
        ]

    paginator = Paginator(pedidos_cliente, 20)

    page = request.GET.get("page")

    pedidos_cliente = paginator.get_page(page)

    return render(
        request,
        "home.html",
        {
            "pedidos": pedidos_cliente,
            "status_disponiveis": status_disponiveis,
        },
    )

from django.contrib import messages

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        print(f"Usuário: {username}")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        print(f"Authenticate: {user}")

        if user is not None:
            login(request, user)
            return redirect('/')

        messages.error(request, "Usuário ou senha inválidos.")

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('/login/')


@login_required
def viesano_insights(request, numero_codop):

    indicadores = consultar_indicadores_producao(numero_codop)

    if not indicadores:
        return render(
            request,
            "viesano_insights.html",
            {
                "indicadores": None,
                "resumo": None,
            },
        )

    resumo = gerar_resumo(indicadores)

    return render(
        request,
        "viesano_insights.html",
        {
            "indicadores": indicadores,
            "resumo": resumo,
        },
    )
    
    
def detalhes_mrp(request, numero_pedido, codigo_produto):

    materiais = mrp(numero_pedido, codigo_produto)
    
    for item in materiais:

        if item["estoque_atual"] < 0:
            item["estoque_cliente"] = 0
        else:
            item["estoque_cliente"] = item["estoque_atual"]

    return render(
        request,
        "mrp.html",
        {
            "materiais": materiais,
            "numero_pedido": numero_pedido
        }
    )