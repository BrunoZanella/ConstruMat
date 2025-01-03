from django.contrib import admin
from .models import Pedido, ItemPedido, Avaliacao

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'empresa', 'status', 'data_pedido']
    list_filter = ['status', 'data_pedido']
    search_fields = ['cliente__username', 'empresa__nome_fantasia']
    inlines = [ItemPedidoInline]

@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'nota', 'data']
    list_filter = ['nota', 'data']
    search_fields = ['pedido__cliente__username', 'comentario']