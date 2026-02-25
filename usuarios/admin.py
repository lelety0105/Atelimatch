"""
Configuração do Django Admin para o app usuarios.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, PessoaPerfil, Atelie


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Admin para CustomUser."""
    
    list_display = ['email', 'is_atelie', 'is_cliente', 'is_staff', 'is_active']
    list_filter = ['is_atelie', 'is_cliente', 'is_staff', 'is_active']
    search_fields = ['email']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Tipo de Usuário', {'fields': ('is_atelie', 'is_cliente')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_atelie', 'is_cliente'),
        }),
    )


@admin.register(PessoaPerfil)
class PessoaPerfilAdmin(admin.ModelAdmin):
    """Admin para PessoaPerfil."""
    
    list_display = ['nome_completo', 'user', 'telefone', 'cidade', 'uf']
    search_fields = ['nome_completo', 'user__email', 'telefone']
    list_filter = ['uf', 'cidade']
    ordering = ['-criado_em']


@admin.register(Atelie)
class AtelieAdmin(admin.ModelAdmin):
    """Admin para Atelie."""
    
    list_display = ['nome_fantasia', 'user', 'telefone_comercial', 'ativo']
    search_fields = ['nome_fantasia', 'user__email', 'cnpj']
    list_filter = ['ativo']
    ordering = ['-criado_em']
