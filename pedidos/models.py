from django.db import models
from usuarios.models import Usuario, Motorista
from empresas.models import Empresa, Produto
from decimal import Decimal
from django.utils import timezone

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('PEN', 'Pendente'),  # Aguardando motorista
        ('ACE', 'Aceito'),    # Motorista aceitou
        ('RET', 'Retirado'),  # Motorista retirou na empresa
        ('SAI', 'Saiu para entrega'),
        ('ENT', 'Entregue'),
        ('CAN', 'Cancelado')
    ]
    
    cliente = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE, related_name='pedidos_cliente')
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE)
    motorista = models.ForeignKey('usuarios.Motorista', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='PEN')
    data_pedido = models.DateTimeField(auto_now_add=True)
    data_aceite = models.DateTimeField(null=True, blank=True)
    data_retirada = models.DateTimeField(null=True, blank=True)
    data_entrega = models.DateTimeField(null=True, blank=True)
    endereco_entrega = models.CharField(max_length=255)
    observacao = models.TextField(blank=True)
    
    def pode_cancelar(self):
        return self.status == 'PEN'
    
    def pode_aceitar(self):
        return self.status == 'PEN' and not self.motorista
    
    def pode_retirar(self):
        return self.status == 'ACE'
    
    def pode_entregar(self):
        return self.status == 'RET'
    
    def cancelar(self):
        if self.pode_cancelar():
            self.status = 'CAN'
            self.save()
            return True
        return False
    
    def aceitar(self, motorista):
        if self.pode_aceitar() and not motorista.tem_pedido_em_andamento():
            self.motorista = motorista
            self.status = 'ACE'
            self.data_aceite = timezone.now()
            self.save()
            return True
        return False
    
    def retirar(self):
        if self.pode_retirar():
            self.status = 'RET'
            self.data_retirada = timezone.now()
            self.save()
            return True
        return False
    
    def entregar(self):
        if self.pode_entregar():
            self.status = 'ENT'
            self.data_entrega = timezone.now()
            self.save()
            return True
        return False

    @property
    def total(self):
        return sum(item.subtotal for item in self.itempedido_set.all())

    @property
    def valor_frete(self):
        # Cálculo básico do frete baseado na distância
        # Você pode implementar uma lógica mais complexa
        return Decimal('20.00')   # Valor fixo para exemplo

    def get_status_class(self):
        classes = {
            'PEN': 'pendente',
            'ACE': 'aceito',
            'PRE': 'preparacao',
            'RET': 'retirado',  
            'SAI': 'saiu',
            'ENT': 'entregue',
            'CAN': 'cancelado',
        }
        return classes.get(self.status, 'default')
    
    class Meta:
        ordering = ['-data_pedido']
    
class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario
    
    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'
    
    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"

class Avaliacao(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)
    nota = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comentario = models.TextField(blank=True)
    data = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'