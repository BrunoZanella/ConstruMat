from django.shortcuts import render
from empresas.models import Empresa, TipoEmpresa, Produto
from django.db.models import Q
from pedidos.models import Pedido
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages



def home(request):

    if request.user.is_authenticated:
        if hasattr(request.user, 'cliente'):
            empresas = Empresa.objects.filter(ativo=True)
            return render(request, 'home.html', {'empresas': empresas})

        elif hasattr(request.user, 'motorista'):
            # Pedidos disponíveis para motoristas
            pedidos = Pedido.objects.filter(
                status='PEN',
                motorista__isnull=True
            ).select_related(
                'empresa', 'cliente'
            ).prefetch_related('itempedido_set__produto').order_by('-data_pedido')

            return render(request, 'home_motorista.html', {'pedidos': pedidos})

        elif hasattr(request.user, 'empresa'):
            # Pedidos da empresa com paginação
            pedidos = Pedido.objects.filter(
                empresa=request.user.empresa
            ).exclude(
                status__in=['ENT', 'CAN']
            ).select_related(
                'cliente', 'motorista'
            ).order_by('-data_pedido')
            
            paginator = Paginator(pedidos, 10)
            page = request.GET.get('page')
            pedidos_paginados = paginator.get_page(page)
            
            return render(request, 'home_empresa.html', {'pedidos': pedidos_paginados})
        
        else:
            empresas = Empresa.objects.filter(ativo=True)
            return render(request, 'home.html', {'empresas': empresas})
            
    # Lista de empresas para clientes e visitantes
    empresas = Empresa.objects.filter(ativo=True)
    return render(request, 'home.html', {'empresas': empresas})


'''
def home(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'cliente'):
            empresas = Empresa.objects.filter(ativo=True)
            return render(request, 'home.html', {'empresas': empresas})

        # Caso o usuário seja um motorista
        elif hasattr(request.user, 'motorista'):
            motorista = request.user.motorista

            # Verificar se o motorista está em uma corrida
            corrida_atual = Pedido.objects.filter(
                motorista=motorista, status__in=['ACE', 'PRE', 'SAI']
            ).select_related('empresa', 'cliente').first()

            if corrida_atual:
                return render(request, 'motoristas/corrida_detalhes.html', {'corrida': corrida_atual})

            # Mostrar pedidos disponíveis caso não esteja em uma corrida
            pedidos_disponiveis = Pedido.objects.filter(
                status='PEN',
                motorista__isnull=True
            ).select_related('empresa', 'cliente').prefetch_related('itempedido_set__produto')

            return render(request, 'home_motorista.html', {'pedidos': pedidos_disponiveis})


        elif hasattr(request.user, 'empresa'):
            # Pedidos da empresa com paginação
            pedidos = Pedido.objects.filter(
                empresa=request.user.empresa
            ).exclude(
                status__in=['ENT', 'CAN']
            ).select_related(
                'cliente', 'motorista'
            ).order_by('-data_pedido')
            
            paginator = Paginator(pedidos, 10)
            page = request.GET.get('page')
            pedidos_paginados = paginator.get_page(page)
            
            return render(request, 'home_empresa.html', {'pedidos': pedidos_paginados})
        
        else:
            empresas = Empresa.objects.filter(ativo=True)
            return render(request, 'home.html', {'empresas': empresas})
            
    # Lista de empresas para clientes e visitantes
    empresas = Empresa.objects.filter(ativo=True)
    return render(request, 'home.html', {'empresas': empresas})

'''


def busca(request):
    query = request.GET.get('q', '')
    tipo_id = request.GET.get('tipo')
    
    resultados = []
    if tipo_id:
        empresas = Empresa.objects.filter(tipo_id=tipo_id, ativo=True)
        resultados = [{'tipo': 'empresa', **empresa.__dict__} for empresa in empresas]
    elif query:
        empresas = Empresa.objects.filter(nome_fantasia__icontains=query, ativo=True)
        produtos = Produto.objects.filter(nome__icontains=query, disponivel=True)
        
        resultados = (
            [{'tipo': 'empresa', **empresa.__dict__} for empresa in empresas] +
            [{'tipo': 'produto', **produto.__dict__} for produto in produtos]
        )
    
    tipos_empresa = TipoEmpresa.objects.all()
    return render(request, 'busca.html', {
        'resultados': resultados,
        'tipos_empresa': tipos_empresa
    })