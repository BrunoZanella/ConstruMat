from django.db import models
from usuarios.models import Usuario
from pedidos.models import Pedido

class Conversa(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    iniciada_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Conversa'
        verbose_name_plural = 'Conversas'

class Mensagem(models.Model):
    conversa = models.ForeignKey(Conversa, on_delete=models.CASCADE)
    remetente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    conteudo = models.TextField()
    enviada_em = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'