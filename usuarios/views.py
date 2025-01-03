from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Max, Q
from django.utils import timezone
from .forms import UsuarioForm, MotoristaForm, PerfilForm
from .models import Motorista
from chat.models import Conversa, Mensagem
from django.contrib.auth import login, logout

def cadastro(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('login')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/cadastro.html', {'form': form})

@login_required
def perfil(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil')
    else:
        form = PerfilForm(instance=request.user)
        
        # Se for motorista, atualiza status para disponível ao logar
        if hasattr(request.user, 'motorista'):
            motorista = request.user.motorista
            if not motorista.disponivel:
                motorista.disponivel = True
                motorista.save()
    
    # Busca conversas do usuário
    conversas = Conversa.objects.filter(
        Q(pedido__cliente=request.user) |
        Q(pedido__empresa__usuario=request.user) |
        Q(pedido__motorista__usuario=request.user)
    ).annotate(
        ultima_mensagem=Max('mensagem__enviada_em'),
        mensagens_nao_lidas=Count(
            'mensagem',
            filter=Q(
                mensagem__lida=False
            ) & ~Q(mensagem__remetente=request.user)  # Corrigido para evitar erro de sintaxe
        )
    ).order_by('-ultima_mensagem')
    
    # Adiciona a última mensagem a cada conversa, caso existam mensagens
    for conversa in conversas:
        if conversa.mensagem_set.exists():  # Verifica se existem mensagens
            conversa.ultima_mensagem = conversa.mensagem_set.latest('enviada_em')
        else:
            conversa.ultima_mensagem = None  # Caso não haja mensagens, define como None

    
    return render(request, 'usuarios/perfil.html', {
        'form': form,
        'conversas': conversas
    })



@login_required
def cadastro_motorista(request):
    if hasattr(request.user, 'motorista'):
        return redirect('perfil')
    
    if request.method == 'POST':
        form = MotoristaForm(request.POST)
        if form.is_valid():
            motorista = form.save(commit=False)
            motorista.usuario = request.user
            motorista.disponivel = True  # Motorista fica disponível ao se cadastrar
            motorista.save()
            messages.success(request, 'Cadastro de motorista realizado com sucesso!')
            return redirect('perfil')
    else:
        form = MotoristaForm()
    
    return render(request, 'motoristas/cadastro.html', {'form': form})

@login_required
def editar_motorista(request):
    motorista = get_object_or_404(Motorista, usuario=request.user)
    
    if request.method == 'POST':
        form = MotoristaForm(request.POST, instance=motorista)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados do motorista atualizados com sucesso!')
            return redirect('perfil')
    else:
        form = MotoristaForm(instance=motorista)
    
    return render(request, 'motoristas/cadastro.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, 'Você saiu!')
    return redirect('home')
