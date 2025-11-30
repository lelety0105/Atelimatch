"""
Configuração do Django Admin para o app ia.
"""

from django.contrib import admin
from .models import PromptImagem


@admin.register(PromptImagem)
class PromptImagemAdmin(admin.ModelAdmin):
    """Admin para PromptImagem."""
    
    list_display = ['usuario', 'prompt_resumido', 'modelo', 'sucesso', 'criado_em']
    list_filter = ['sucesso', 'modelo', 'criado_em']
    search_fields = ['usuario__email', 'prompt']
    ordering = ['-criado_em']
    readonly_fields = ['criado_em']
    
    def prompt_resumido(self, obj):
        """Retorna versão resumida do prompt."""
        return obj.prompt[:50] + '...' if len(obj.prompt) > 50 else obj.prompt
    
    prompt_resumido.short_description = 'Prompt'
