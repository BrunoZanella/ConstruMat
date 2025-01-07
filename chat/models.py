from django.db import models
from django.db.models import Q
from django.utils import timezone

class Conversa(models.Model):
    TIPO_CHOICES = [
        ('CLI_EMP', 'Cliente-Empresa'),
        ('CLI_MOT', 'Cliente-Motorista'),
        ('MOT_EMP', 'Motorista-Empresa'),
    ]
    
    pedido = models.ForeignKey('pedidos.Pedido', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)
    iniciada_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Conversa'
        verbose_name_plural = 'Conversas'
        unique_together = ['pedido', 'tipo']
    
    def get_participantes(self):
        """Retorna os usuários participantes da conversa"""
        if self.tipo == 'CLI_EMP':
            return [self.pedido.cliente, self.pedido.empresa.usuario]
        elif self.tipo == 'CLI_MOT':
            return [self.pedido.cliente, self.pedido.motorista.usuario]
        elif self.tipo == 'MOT_EMP':
    #    else:  # MOT_EMP
            return [self.pedido.motorista.usuario, self.pedido.empresa.usuario]
    
    def pode_participar(self, usuario):
        """Verifica se o usuário pode participar da conversa"""
        return usuario in self.get_participantes()
    
    @property
    def ultima_mensagem(self):
        return self.mensagem_set.order_by('-enviada_em').first()
    
    @property
    def total_nao_lidas(self):
        """Agora verifica as mensagens não lidas para um usuário específico."""
        return self.mensagem_set.filter(lida=False).exclude(remetente__in=self.get_participantes()).count()

class Mensagem(models.Model):
    conversa = models.ForeignKey(Conversa, on_delete=models.CASCADE)
    remetente = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)
    conteudo = models.TextField()
    enviada_em = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'
        ordering = ['enviada_em']
    
    def save(self, *args, **kwargs):
        # Verifica se o remetente pode participar da conversa
        if not self.conversa.pode_participar(self.remetente):
            raise ValueError("O usuário não pode participar desta conversa")
        super().save(*args, **kwargs)