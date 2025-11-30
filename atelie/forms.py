"""
Forms do app atelie.
"""

from django import forms
from .models import Produto, EstoqueItem, Pedido, ItemPedido, Servico


class ProdutoForm(forms.ModelForm):
    """Form para Produto."""

    class Meta:
        model = Produto
        fields = ['nome', 'categoria', 'preco_base', 'descricao', 'ativo']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
        }


class ServicoForm(forms.ModelForm):
    """Form para Servico."""

    class Meta:
        model = Servico
        fields = ['nome', 'descricao', 'preco_base', 'duracao_estimada', 'ativo']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
        }


class EstoqueItemForm(forms.ModelForm):
    """Form para EstoqueItem."""

    class Meta:
        model = EstoqueItem
        fields = ['produto', 'quantidade_atual', 'ponto_reposicao']


class PedidoForm(forms.ModelForm):
    """Form para Pedido."""

    class Meta:
        model = Pedido
        fields = ['cliente', 'atelie', 'tipo_servico', 'status', 'data_agendada', 'hora_agendada', 'observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'data_agendada': forms.DateInput(attrs={'type': 'date'}),
            'hora_agendada': forms.TimeInput(attrs={'type': 'time'}),
        }


class PedidoClienteEditForm(forms.ModelForm):
    """Form de edição que será mostrado ao cliente. Limita campos editáveis pelo cliente."""

    class Meta:
        model = Pedido
        fields = ['data_agendada', 'hora_agendada', 'observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'data_agendada': forms.DateInput(attrs={'type': 'date'}),
            'hora_agendada': forms.TimeInput(attrs={'type': 'time'}),
        }


class PedidoAtelieEditForm(forms.ModelForm):
    """Form de edição para o ateliê. Permite alterar prazos, observações, status e tipo de serviço."""

    class Meta:
        model = Pedido
        fields = ['tipo_servico', 'status', 'data_agendada', 'hora_agendada', 'observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 4}),
            'data_agendada': forms.DateInput(attrs={'type': 'date'}),
            'hora_agendada': forms.TimeInput(attrs={'type': 'time'}),
        }


class ItemPedidoForm(forms.ModelForm):
    """Form para ItemPedido."""

    class Meta:
        model = ItemPedido
        fields = ['produto', 'servico', 'qtde', 'preco_unitario']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' not in kwargs and 'initial' not in kwargs:
            self.fields['preco_unitario'].widget.attrs['readonly'] = False
