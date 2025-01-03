from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Motorista

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'tipo', 'telefone', 'is_active']
    list_filter = ['tipo', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('tipo', 'telefone', 'foto')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('tipo', 'telefone', 'foto')}),
    )

@admin.register(Motorista)
class MotoristaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo_veiculo', 'placa', 'disponivel']
    list_filter = ['tipo_veiculo', 'disponivel']
    search_fields = ['usuario__username', 'placa', 'cnh']