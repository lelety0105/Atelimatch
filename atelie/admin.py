# atelie/admin.py

from django.contrib import admin

from .models import (
    Produto,
    EstoqueItem,
    Pedido,
    ItemPedido,
    Servico,
    ChatMensagem,
)


class ItemPedidoInline(admin.TabularInline):
    """
    Inline para itens de pedido dentro do admin de Pedido.
    """
    model = ItemPedido
    extra = 0
    fields = ("produto", "servico", "qtde", "preco_unitario", "subtotal_display")
    readonly_fields = ("subtotal_display",)

    def subtotal_display(self, obj):
        """
        Mostra o subtotal calculado (preco_unitario * qtde).
        Se o objeto ainda não foi salvo, mostra apenas um traço.
        """
        if obj.pk:
            return obj.subtotal
        return "-"

    subtotal_display.short_description = "Subtotal"


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    """
    Admin para Produto.
    """
    list_display = ("nome", "categoria", "preco_base", "ativo", "criado_em")
    list_filter = ("categoria", "ativo", "criado_em")
    search_fields = ("nome", "descricao")
    list_editable = ("ativo",)
    ordering = ("-criado_em",)


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    """
    Admin para Servico.
    """
    list_display = ("nome", "preco_base", "duracao_estimada", "ativo", "criado_em")
    list_filter = ("ativo", "criado_em")
    search_fields = ("nome", "descricao")
    ordering = ("-criado_em",)


@admin.register(EstoqueItem)
class EstoqueItemAdmin(admin.ModelAdmin):
    """
    Admin para EstoqueItem.
    """
    list_display = (
        "produto",
        "quantidade_atual",
        "ponto_reposicao",
        "precisa_repor",
        "atualizado_em",
    )
    list_filter = ("produto__categoria", "produto__ativo")
    search_fields = ("produto__nome",)
    autocomplete_fields = ("produto",)

    def precisa_repor(self, obj):
        """
        Usa a property do modelo para indicar se está em ponto de reposição.
        """
        return obj.precisa_reposicao

    precisa_repor.boolean = True
    precisa_repor.short_description = "Precisa repor?"


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """
    Admin para Pedido.
    """
    list_display = (
        "id",
        "cliente",
        "atelie",
        "status",
        "tipo_servico",
        "valor_total",
        "data_agendada",
        "hora_agendada",
        "criado_em",
    )
    list_filter = (
        "status",
        "tipo_servico",
        "atelie",
        "criado_em",
        "data_agendada",
    )
    search_fields = (
        "id",
        "cliente__email",
        "cliente__pessoaperfil__nome_completo",
        "atelie__nome_fantasia",
    )
    date_hierarchy = "criado_em"
    autocomplete_fields = ("cliente", "atelie")
    inlines = [ItemPedidoInline]


@admin.register(ChatMensagem)
class ChatMensagemAdmin(admin.ModelAdmin):
    """
    Admin para ChatMensagem.
    """
    list_display = ("pedido", "autor", "criado_em", "lida_por_cliente", "lida_por_atelie")
    list_filter = ("lida_por_cliente", "lida_por_atelie", "criado_em")
    search_fields = ("pedido__id", "autor__email", "conteudo")
    autocomplete_fields = ("pedido", "autor")
