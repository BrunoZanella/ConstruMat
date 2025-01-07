from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class Usuario(AbstractUser):
    TIPO_USUARIO = (
        ('CLI', 'Cliente'),
        ('MOT', 'Motorista'),
        ('EMP', 'Empresa'),
    )

    tipo = models.CharField(max_length=3, choices=TIPO_USUARIO)
    telefone = PhoneNumberField(unique=True)
    foto = models.ImageField(upload_to='usuarios/', null=True, blank=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def tem_notificacoes(self):
        from pedidos.models import Pedido
        if hasattr(self, 'empresa'):
            return Pedido.objects.filter(
                empresa=self.empresa,
                conversa__mensagem__lida=False
            ).exclude(
                conversa__mensagem__remetente=self
            ).exists()
        else:
            return Pedido.objects.filter(
                cliente=self,
                conversa__mensagem__lida=False
            ).exclude(
                conversa__mensagem__remetente=self
            ).exists()

    def total_notificacoes(self):
        from pedidos.models import Pedido
        if hasattr(self, 'empresa'):
            pedidos = Pedido.objects.filter(empresa=self.empresa)
        else:
            pedidos = Pedido.objects.filter(cliente=self)
        
        return pedidos.filter(
            conversa__mensagem__lida=False
        ).exclude(
            conversa__mensagem__remetente=self
        ).count()
        
        
class Motorista(models.Model):
    TIPO_VEICULO = (
        ('CAR', 'Carro'),
        ('VAN', 'Van'),
        ('CAM', 'Caminhão'),
    )
    
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    cnh = models.CharField('CNH', max_length=11)
    tipo_veiculo = models.CharField('Tipo de Veículo', max_length=3, choices=TIPO_VEICULO)
    placa = models.CharField(max_length=7)
    disponivel = models.BooleanField('Disponível', default=True)

    def tem_pedido_em_andamento(self):
        return self.pedido_set.filter(
            status__in=['ACE', 'RET', 'SAI']
        ).exists()
        
    class Meta:
        verbose_name = 'Motorista'
        verbose_name_plural = 'Motoristas'

    def __str__(self):
        return f"{self.usuario}"