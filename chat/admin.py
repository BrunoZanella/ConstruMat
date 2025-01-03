from django.contrib import admin
from .models import Conversa, Mensagem

class MensagemInline(admin.TabularInline):
    model = Mensagem
    extra = 0

@admin.register(Conversa)
class ConversaAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'iniciada_em']
    search_fields = ['pedido__cliente__username']
    inlines = [MensagemInline]

@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ['conversa', 'remetente', 'enviada_em', 'lida']
    list_filter = ['lida', 'enviada_em']
    search_fields = ['remetente__username', 'conteudo']