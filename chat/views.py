from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Conversa, Mensagem
from pedidos.models import Pedido

@login_required
def conversa_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Verifica se o usuário tem permissão para acessar o chat
    if request.user not in [pedido.cliente, pedido.empresa.usuario] and \
       (pedido.motorista and request.user != pedido.motorista.usuario):
        messages.error(request, 'Você não tem permissão para acessar este chat.')
        return redirect('pedidos')
    
    conversa, _ = Conversa.objects.get_or_create(pedido=pedido)
    
    # Marca mensagens não lidas como lidas
    Mensagem.objects.filter(conversa=conversa, lida=False).exclude(remetente=request.user).update(lida=True)
    
    if request.method == 'POST':
        conteudo = request.POST.get('mensagem')
        if conteudo:
            Mensagem.objects.create(
                conversa=conversa,
                remetente=request.user,
                conteudo=conteudo
            )
    
    mensagens = conversa.mensagem_set.all().order_by('enviada_em')
    return render(request, 'chat/conversa.html', {
        'pedido': pedido,
        'mensagens': mensagens
    })
