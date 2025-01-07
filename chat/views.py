from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Conversa, Mensagem
from .services import ChatService
from pedidos.models import Pedido
import time

@login_required
def lista_conversas(request):
    """Lista todas as conversas do usuário"""
    conversas = ChatService.get_conversas_usuario(request.user)
    
    # Calcula as mensagens não lidas para cada conversa
    for conversa in conversas:
        conversa.nao_lidas = conversa.total_nao_lidas
    
    return render(request, 'chat/lista_conversas.html', {
        'conversas': conversas
    })

@login_required
def conversa_pedido(request, pedido_id):

    """Exibe, gerencia e possibilita iniciar uma nova conversa específica"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Verifica se o usuário pode acessar o pedido
    if request.user not in [
        pedido.cliente,
        pedido.empresa.usuario,
        getattr(pedido.motorista, 'usuario', None)
    ]:
        messages.error(request, 'Você não tem permissão para acessar esta conversa.')
        return redirect('pedidos')
    
    # Determina os tipos de conversa disponíveis
    tipos_conversa = {
        'CLI_EMP': 'Cliente ↔ Empresa',
        'CLI_MOT': 'Cliente ↔ Motorista',
        'MOT_EMP': 'Motorista ↔ Empresa',
    }


#    tipo = request.GET.get('tipo', 'CLI_EMP')  # Define um tipo padrão
    tipo = request.GET.get('tipo', None)
    if tipo == None:
        # Define o tipo baseado no usuário logado
        if request.user == pedido.cliente:
            tipo = 'CLI_EMP'  # Cliente pode conversar com a Empresa
        elif request.user == pedido.motorista:
            tipo = 'CLI_MOT'  # Motorista pode conversar com o Cliente
        else:
            tipo = 'CLI_EMP'  # Empresa pode conversar com o Motorista ou Cliente
        

    conversas = ChatService.get_conversas_disponiveis(pedido, request.user)
    
    # Cria conversas automaticamente para garantir que os botões funcionem
    for t in tipos_conversa:
        if not conversas.filter(tipo=t).exists():
            if (
                (t == 'CLI_EMP' and pedido.cliente and pedido.empresa.usuario) or
                (t == 'CLI_MOT' and pedido.cliente and pedido.motorista) or
                (t == 'MOT_EMP' and pedido.empresa.usuario and pedido.motorista)
            ):
                Conversa.objects.get_or_create(pedido=pedido, tipo=t)
    
    # Verifica se a conversa já existe
    conversa = Conversa.objects.filter(pedido=pedido, tipo=tipo).first()

    if not conversa:
        # Se não existir uma conversa, cria uma nova
        conversa = Conversa.objects.create(pedido=pedido, tipo=tipo)

    
    # Processa envio de mensagem
    if request.method == 'POST':
        conteudo = request.POST.get('mensagem')
        if conteudo:
            ChatService.enviar_mensagem(conversa, request.user, conteudo)
            return redirect('chat_pedido', pedido_id=pedido_id)
    
    # Marca mensagens como lidas
    if conversa:
        ChatService.marcar_como_lidas(conversa, request.user)
    
    return render(request, 'chat/conversa.html', {
        'pedido': pedido,
        'conversa': conversa,
        'mensagens': conversa.mensagem_set.all() if conversa else [],
        'tipo_atual': tipo,
        'tipos_conversa': tipos_conversa,
    })




@login_required
def atualizar_mensagens(request, conversa_id):
    """Endpoint AJAX para atualizar mensagens"""
    conversa = get_object_or_404(Conversa, id=conversa_id)
    
    if not conversa.pode_participar(request.user):
        return JsonResponse({'error': 'Não autorizado'}, status=403)
    
    ultima_msg_id = request.GET.get('ultima_msg')
    novas_mensagens = conversa.mensagem_set.filter(id__gt=ultima_msg_id) if ultima_msg_id else []
    
    # Marca novas mensagens como lidas
    ChatService.marcar_como_lidas(conversa, request.user)
    return JsonResponse({
        'mensagens': [{
            'id': msg.id,
            'conteudo': msg.conteudo,
            'remetente': msg.remetente.get_full_name() or msg.remetente.username,
            'enviada_em': msg.enviada_em.strftime('%H:%M'),
            'is_own': msg.remetente == request.user
        } for msg in novas_mensagens]
    })