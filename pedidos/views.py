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

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('/')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('/login/')