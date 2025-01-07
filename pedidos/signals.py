from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pedido
from chat.services import ChatService

@receiver(post_save, sender=Pedido)
def criar_conversas_pedido(sender, instance, created, **kwargs):
    """Cria as conversas necessárias quando um pedido é criado ou atualizado"""
    if created:
        # Cria conversa entre cliente e empresa
        ChatService.iniciar_conversas_pedido(instance)
    elif instance.motorista_id and instance.status == 'ACE':
        # Cria conversas relacionadas ao motorista quando ele aceita o pedido
        ChatService.iniciar_conversas_motorista(instance)