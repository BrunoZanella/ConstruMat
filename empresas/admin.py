from django.contrib import admin
from .models import TipoEmpresa, Empresa, Produto

@admin.register(TipoEmpresa)
class TipoEmpresaAdmin(admin.ModelAdmin):
    list_display = ['nome']

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['nome_fantasia', 'tipo', 'cnpj', 'ativo']
    list_filter = ['tipo', 'ativo']
    search_fields = ['nome_fantasia', 'razao_social', 'cnpj']

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'empresa', 'preco', 'disponivel']
    list_filter = ['empresa', 'disponivel']
    search_fields = ['nome', 'empresa__nome_fantasia']