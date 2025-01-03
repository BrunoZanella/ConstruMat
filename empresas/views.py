from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Max, Q
from django.utils import timezone
from .models import Empresa, Produto
from chat.models import Conversa, Mensagem
from usuarios.models import Motorista
from .forms import EmpresaForm, ProdutoForm
from usuarios.forms import UsuarioForm, MotoristaForm, PerfilForm

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

@login_required
def cadastro_empresa(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST, request.FILES)
        if form.is_valid():
            empresa = form.save(commit=False)
            empresa.usuario = request.user
            empresa.save()
            messages.success(request, 'Empresa cadastrada com sucesso!')
            return redirect('empresa_detalhes', empresa.id)
    else:
        form = EmpresaForm()
    return render(request, 'empresas/cadastro.html', {'form': form})


@login_required
def editar_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id, usuario=request.user)
    if request.method == 'POST':
        form = EmpresaForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empresa atualizada com sucesso!')
            return redirect('perfil')
    else:
        form = EmpresaForm(instance=empresa)
    return render(request, 'empresas/form_empresa.html', {'form': form, 'empresa': empresa})

def empresa_detalhes(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id, ativo=True)
    
    # Verifica se a empresa está aberta
    agora = timezone.localtime().time()
    empresa.esta_aberta = empresa.hora_abertura <= agora <= empresa.hora_fechamento
    
    produtos = Produto.objects.filter(empresa=empresa, disponivel=True)
    return render(request, 'empresas/detalhes.html', {
        'empresa': empresa,
        'produtos': produtos
    })


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
                mensagem__lida=False,
                mensagem__remetente__ne=request.user
            )
        )
    ).order_by('-ultima_mensagem')
    
    # Adiciona a última mensagem a cada conversa
    for conversa in conversas:
        conversa.ultima_mensagem = conversa.mensagem_set.latest('enviada_em')
    
    return render(request, 'usuarios/perfil.html', {
        'form': form,
        'conversas': conversas
    })
    

@login_required
def gerenciar_produtos(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id, usuario=request.user)
    produtos = Produto.objects.filter(empresa=empresa)
    return render(request, 'empresas/gerenciar_produtos.html', {
        'empresa': empresa,
        'produtos': produtos
    })


@login_required
def novo_produto(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id, usuario=request.user)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.empresa = empresa
            produto.save()
            messages.success(request, 'Produto adicionado com sucesso!')
            return redirect('gerenciar_produtos', empresa.id)
    else:
        form = ProdutoForm()
    return render(request, 'empresas/form_produto.html', {
        'form': form,
        'empresa': empresa
    })


@login_required
def editar_produto(request, empresa_id, produto_id):
    empresa = get_object_or_404(Empresa, id=empresa_id, usuario=request.user)
    produto = get_object_or_404(Produto, id=produto_id, empresa=empresa)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('gerenciar_produtos', empresa.id)
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'empresas/form_produto.html', {
        'form': form,
        'empresa': empresa,
        'produto': produto
    })