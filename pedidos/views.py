from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Pedido, ItemPedido, Avaliacao
from .forms import PedidoForm, AvaliacaoForm, ItemPedidoForm
from empresas.models import Empresa, Produto
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse

'''
@login_required
def lista_pedidos(request):
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-data_pedido')
    return render(request, 'pedidos/lista.html', {'pedidos': pedidos})
'''

@login_required
def lista_pedidos(request):
    # Verificar se o usuário é da empresa
    if hasattr(request.user, 'empresa'):
        empresa = request.user.empresa
        pedidos = Pedido.objects.filter(empresa=empresa).order_by('-data_pedido')  # Todos os pedidos da empresa
    elif hasattr(request.user, 'motorista'):
        pedidos = Pedido.objects.filter(motorista__usuario=request.user).order_by('-data_pedido')

    else:
        pedidos = Pedido.objects.filter(cliente=request.user).order_by('-data_pedido')  # Pedidos do cliente

    return render(request, 'pedidos/lista.html', {'pedidos': pedidos})


@login_required
def novo_pedido(request, empresa_id):
    try:
        empresa = Empresa.objects.get(id=empresa_id)
    except Empresa.DoesNotExist:
        messages.error(request, 'Empresa não encontrada.')
        return redirect('empresas')

    produto_id = request.GET.get('produto')
    produto = Produto.objects.filter(id=produto_id).first()

    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.cliente = request.user
            pedido.empresa = empresa
            pedido.save()
            if produto:
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    quantidade=1,
                    preco_unitario=produto.preco
                )
            messages.success(request, 'Pedido realizado com sucesso!')
            return redirect('detalhes_pedido', pedido.id)
    else:
        form = PedidoForm()

    return render(request, 'pedidos/novo.html', {
        'form': form,
        'empresa': empresa,
        'produto': produto,
    })



@login_required
def detalhes_pedido(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        
        # Verificar se o usuário é o cliente ou está associado à empresa
        if pedido.cliente == request.user or pedido.empresa.usuario == request.user:
            return render(request, 'pedidos/detalhes.html', {'pedido': pedido})
        else:
            messages.error(request, "Você não tem permissão para acessar este pedido.")
            return redirect('pedidos')
    
    except Pedido.DoesNotExist:
        messages.error(request, "Pedido não encontrado.")
        return redirect('pedidos')


@login_required
def avaliar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, status='ENT')
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.pedido = pedido
            avaliacao.save()
            messages.success(request, 'Avaliação enviada com sucesso!')
            return redirect('pedidos')
    return redirect('pedidos')


@login_required
def pedidos_motorista(request):
    if not hasattr(request.user, 'motorista'):
        messages.error(request, 'Você precisa ser um motorista cadastrado.')
        return redirect('home')
    
    pedidos = Pedido.objects.filter(
        status='PEN'
    ).exclude(
        motorista__isnull=False
    ).order_by('-data_pedido')
    
    return render(request, 'pedidos/motorista/lista.html', {'pedidos': pedidos})




'''
@login_required
def aceitar_pedido(request, pedido_id):
    if not hasattr(request.user, 'motorista'):
        messages.error(request, 'Você precisa ser um motorista cadastrado.')
        return redirect('home')
    
    pedido = get_object_or_404(Pedido, id=pedido_id, status='PEN', motorista__isnull=True)
    pedido.motorista = request.user.motorista
    pedido.status = 'ACE'
    pedido.save()
    
    messages.success(request, 'Pedido aceito com sucesso!')
    return redirect('pedidos_motorista')

'''


def aceitar_pedido(request, pedido_id):
    if request.user.is_authenticated and hasattr(request.user, 'motorista'):
        motorista = request.user.motorista

        # Verificar se o motorista já está em uma corrida
        if Pedido.objects.filter(motorista=motorista, status__in=['ACE', 'PRE', 'SAI']).exists():
            messages.error(request, "Você já está em uma corrida. Conclua-a antes de aceitar outra.")
            return HttpResponseRedirect(reverse('home'))

        # Associar motorista ao pedido e alterar status
        pedido = get_object_or_404(Pedido, id=pedido_id, status='PEN', motorista__isnull=True)
        pedido.motorista = motorista
        pedido.status = 'ACE'
        pedido.save()

        messages.success(request, f"Corrida aceita! Você está agora na corrida do pedido #{pedido.id}.")
        return HttpResponseRedirect(reverse('home'))
    return HttpResponseRedirect(reverse('login'))

@login_required
def concluir_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, motorista__usuario=request.user)
    
    if pedido.status != 'SAI':
        messages.error(request, 'Este pedido não está em entrega.')
        return redirect('pedidos_motorista')
    
    if request.method == 'POST':
        pedido.status = 'ENT'
        pedido.save()
        
        # Gera recibo
        recibo = {
            'pedido': pedido,
            'data_entrega': timezone.now(),
            'itens': pedido.itempedido_set.all(),
            'total': pedido.total,
            'frete': pedido.valor_frete,
            'total_com_frete': pedido.total + pedido.valor_frete
        }
        
        return render(request, 'pedidos/recibo.html', {'recibo': recibo})
    
    return render(request, 'pedidos/confirmar_entrega.html', {'pedido': pedido})








def atualizar_status_corrida(request, pedido_id, novo_status):
    pedido = get_object_or_404(Pedido, id=pedido_id, motorista=request.user.motorista)

    # Define as transições permitidas
    status_permitidos = {
        'ACE': ['PRE', 'CAN'],
        'PRE': ['SAI', 'CAN'],
        'SAI': ['ENT', 'CAN'],
    }

    # Verificar se a transição é válida
    if novo_status in status_permitidos.get(pedido.status, []):
        pedido.status = novo_status
        pedido.save()
        messages.success(request, f"Status atualizado para {novo_status}.")
        return JsonResponse({'success': True, 'novo_status': novo_status})

    # Caso a transição não seja válida
    return JsonResponse({'success': False, 'error': 'Transição de status inválida.'}, status=400)

