from django.db import transaction
from .models import Conversa, Mensagem
from django.db.models import Count, Max, Q

class ChatService:
    
    @staticmethod
    def criar_ou_obter_conversa(pedido, tipo):
        """Cria ou obtém uma conversa existente"""
        conversa, _ = Conversa.objects.get_or_create(
            pedido=pedido,
            tipo=tipo
        )
        return conversa
    
    @staticmethod
    def iniciar_conversas_pedido(pedido):
        """Inicia a conversa entre cliente e empresa quando o pedido é criado"""
        return ChatService.criar_ou_obter_conversa(pedido, 'CLI_EMP')
    
    @staticmethod
    def iniciar_conversas_motorista(pedido):
        """Inicia as conversas relacionadas ao motorista quando ele aceita o pedido"""
        with transaction.atomic():
            ChatService.criar_ou_obter_conversa(pedido, 'CLI_MOT')
            ChatService.criar_ou_obter_conversa(pedido, 'MOT_EMP')
    
    @staticmethod
    def enviar_mensagem(conversa, remetente, conteudo):
        """Envia uma nova mensagem na conversa"""
        return Mensagem.objects.create(
            conversa=conversa,
            remetente=remetente,
            conteudo=conteudo
        )
    
    @staticmethod
    def marcar_como_lidas(conversa, usuario):
        """Marca todas as mensagens não lidas como lidas para um usuário"""
        Mensagem.objects.filter(
            conversa=conversa,
            lida=False
        ).exclude(
            remetente=usuario
        ).update(lida=True)
    
    @staticmethod
    def get_conversas_usuario(usuario):
        """Retorna apenas as conversas que o usuário deve ver"""
        if hasattr(usuario, 'empresa'):
            # Para empresa: apenas conversas CLI_EMP e MOT_EMP
            return Conversa.objects.filter(
                pedido__empresa__usuario=usuario,
                tipo__in=['CLI_EMP', 'MOT_EMP']
            )
        elif hasattr(usuario, 'motorista'):
            # Para motorista: apenas conversas CLI_MOT e MOT_EMP
            return Conversa.objects.filter(
                pedido__motorista__usuario=usuario,
                tipo__in=['CLI_MOT', 'MOT_EMP']
            )
        elif hasattr(usuario, 'cliente'):
#        else:
            # Para cliente: apenas conversas CLI_EMP e CLI_MOT
            return Conversa.objects.filter(
                pedido__cliente=usuario,
                tipo__in=['CLI_EMP', 'CLI_MOT']
            )

    @staticmethod
    def get_conversas_disponiveis(pedido, usuario):
        """Retorna apenas as conversas disponíveis para o usuário no pedido"""
        if usuario == pedido.empresa.usuario:
            # Empresa vê conversas com cliente e motorista (se existir)
            conversas = Q(tipo='CLI_EMP')  # Cliente
            if pedido.motorista:
                conversas |= Q(tipo='MOT_EMP')  # Motorista
        elif usuario == getattr(pedido.motorista, 'usuario', None):
            # Motorista vê conversas com cliente e empresa
            conversas = Q(tipo='CLI_MOT')  # Cliente
            if pedido.empresa:
                conversas |= Q(tipo='MOT_EMP')  # Empresa
        elif usuario == pedido.cliente:
    #    else:
            # Cliente vê conversas com empresa e motorista (se existir)
            conversas = Q(tipo='CLI_EMP')  # Empresa
            if pedido.motorista:
                conversas |= Q(tipo='CLI_MOT')  # Motorista
            
        return Conversa.objects.filter(pedido=pedido).filter(conversas)
