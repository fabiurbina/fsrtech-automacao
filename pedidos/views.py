from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from .mysql_service import consultar_pedidos_cliente
from .status_service import interpretar_status


@login_required
def home(request):

    cpf_cnpj = request.user.username

    print("CPF logado:", cpf_cnpj)

    pedidos = consultar_pedidos_cliente(cpf_cnpj)
    
    pedidos_cliente = []

    for pedido in pedidos:

        status = interpretar_status(
            pedido["descricao_etapa"],
            pedido["status_producao"],
            
            
        )

        pedido["titulo"] = status["titulo"]
        pedido["descricao"] = status["descricao"]
        pedido["cor"] = status["cor"]
        
    

        pedidos_cliente.append(pedido)

    return render(

        request,

        "home.html",

        {

            "pedidos": pedidos_cliente

        }

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