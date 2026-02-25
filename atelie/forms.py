"""
Forms do app atelie.
"""

from django import forms

from .models import ItemPedido, Pedido, Produto, Servico, EstoqueItem


class ProdutoForm(forms.ModelForm):
    """Form para Produto."""

    class Meta:
        model = Produto
        fields = ["nome", "categoria", "preco_base", "descricao", "ativo"]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 4}),
        }


class ServicoForm(forms.ModelForm):
    """Form para Servico."""

    class Meta:
        model = Servico
        fields = ["nome", "descricao", "preco_base", "duracao_estimada", "ativo"]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 4}),
        }


class EstoqueItemForm(forms.ModelForm):
    """Form para EstoqueItem."""

    class Meta:
        model = EstoqueItem
        fields = ["produto", "quantidade_atual", "ponto_reposicao"]

    def __init__(self, *args, **kwargs):
        atelie = kwargs.pop("atelie", None)
        super().__init__(*args, **kwargs)
        qs = Produto.objects.filter(ativo=True)
        if atelie is not None:
            qs = qs.filter(atelie=atelie)
        self.fields["produto"].queryset = qs


class PedidoForm(forms.ModelForm):
    """Form para Pedido."""

    class Meta:
        model = Pedido
        fields = [
            "cliente",
            "atelie",
            "tipo_servico",
            "descricao_cliente",
            "status",
            "data_agendada",
            "hora_agendada",
            "observacoes",
        ]
        widgets = {
            "descricao_cliente": forms.Textarea(attrs={"rows": 4}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
            "data_agendada": forms.DateInput(attrs={"type": "date"}),
            "hora_agendada": forms.TimeInput(attrs={"type": "time"}),
        }


class PedidoClienteEditForm(forms.ModelForm):
    """
    Form de edicao mostrado ao cliente.
    Permite ajustar tipo/descricao do servico
    e tambem o produto/servico associados ao pedido.
    """

    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(ativo=True),
        required=False,
        label="Produto",
    )
    servico = forms.ModelChoiceField(
        queryset=Servico.objects.filter(ativo=True),
        required=False,
        label="Servico",
    )

    class Meta:
        model = Pedido
        fields = [
            "tipo_servico",
            "descricao_cliente",
            "data_agendada",
            "hora_agendada",
            "observacoes",
        ]
        widgets = {
            "descricao_cliente": forms.Textarea(attrs={"rows": 4}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
            "data_agendada": forms.DateInput(attrs={"type": "date"}),
            "hora_agendada": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if instance and instance.pk:
            item_prod = (
                instance.itens.filter(produto__isnull=False)
                .select_related("produto")
                .first()
            )
            item_serv = (
                instance.itens.filter(servico__isnull=False)
                .select_related("servico")
                .first()
            )
            if item_prod:
                self.fields["produto"].initial = item_prod.produto
            if item_serv:
                self.fields["servico"].initial = item_serv.servico

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo_servico")
        descricao = (cleaned_data.get("descricao_cliente") or "").strip()
        produto = cleaned_data.get("produto")
        servico = cleaned_data.get("servico")

        if tipo == "OUTROS" and not descricao:
            self.add_error(
                "descricao_cliente",
                'Descreva o servico quando selecionar "Outros".',
            )

        if not produto and not servico:
            raise forms.ValidationError(
                "Selecione ao menos um produto ou servico."
            )

        return cleaned_data

    def save_items(self, pedido: Pedido) -> None:
        """
        Atualiza os itens (produto/servico) do pedido com base
        nos dados limpos do formulario.
        Mantem no maximo um item de produto e um de servico.
        """

        produto = self.cleaned_data.get("produto")
        servico = self.cleaned_data.get("servico")

        # Produto
        qs_prod = pedido.itens.filter(produto__isnull=False)
        if produto:
            item_prod = qs_prod.first()
            if item_prod:
                item_prod.produto = produto
                item_prod.preco_unitario = produto.preco_base
                item_prod.qtde = 1
                item_prod.save()
                qs_prod.exclude(pk=item_prod.pk).delete()
            else:
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    qtde=1,
                    preco_unitario=produto.preco_base,
                )
        else:
            qs_prod.delete()

        # Servico
        qs_serv = pedido.itens.filter(servico__isnull=False)
        if servico:
            item_serv = qs_serv.first()
            if item_serv:
                item_serv.servico = servico
                item_serv.preco_unitario = servico.preco_base
                item_serv.qtde = 1
                item_serv.save()
                qs_serv.exclude(pk=item_serv.pk).delete()
            else:
                ItemPedido.objects.create(
                    pedido=pedido,
                    servico=servico,
                    qtde=1,
                    preco_unitario=servico.preco_base,
                )
        else:
            qs_serv.delete()


class PedidoAtelieEditForm(forms.ModelForm):
    """
    Form de edicao para o atelie.
    Permite alterar prazos, observacoes, status e dados financeiros.
    """

    class Meta:
        model = Pedido
        fields = ["valor_orcado", "prazo_entrega", "status", "observacoes"]
        widgets = {
            "valor_orcado": forms.NumberInput(attrs={"step": "0.01"}),
            "prazo_entrega": forms.DateInput(attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 4}),
        }


class ItemPedidoForm(forms.ModelForm):
    """Form para ItemPedido."""

    class Meta:
        model = ItemPedido
        fields = ["produto", "servico", "qtde", "preco_unitario"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "instance" not in kwargs and "initial" not in kwargs:
            self.fields["preco_unitario"].widget.attrs["readonly"] = False
