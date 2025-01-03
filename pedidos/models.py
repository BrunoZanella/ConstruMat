from django.db import models
from usuarios.models import Usuario, Motorista
from empresas.models import Empresa, Produto

class Pedido(models.Model):
    STATUS_PEDIDO = (
        ('PEN', 'Pendente'),
        ('ACE', 'Aceito'),
        ('PRE', 'Em Preparação'),
        ('SAI', 'Saiu para Entrega'),
        ('ENT', 'Entregue'),
        ('CAN', 'Cancelado'),
    )
    
    cliente = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)
    motorista = models.ForeignKey(Motorista, on_delete=models.PROTECT, null=True, blank=True)
    status = models.CharField(max_length=3, choices=STATUS_PEDIDO, default='PEN')
    endereco_entrega = models.CharField('Endereço de Entrega', max_length=200)
    data_pedido = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    observacao = models.TextField('Observação', blank=True)
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.username}"

    def tem_mensagens_nao_lidas(self):
        return self.conversa_set.filter(
            mensagem__lida=False
        ).exclude(
            mensagem__remetente=self.empresa.usuario
        ).exists()

    @property
    def total(self):
        return sum(item.subtotal for item in self.itempedido_set.all())

    @property
    def valor_frete(self):
        # Cálculo básico do frete baseado na distância
        # Você pode implementar uma lógica mais complexa
        return 20.00  # Valor fixo para exemplo

    def get_status_class(self):
        classes = {
            'PEN': 'pendente',
            'ACE': 'aceito',
            'PRE': 'preparacao',
            'SAI': 'saiu',
            'ENT': 'entregue',
            'CAN': 'cancelado',
        }
        return classes.get(self.status, 'default')
    
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