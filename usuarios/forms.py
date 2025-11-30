"""
Forms do app usuarios.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, PessoaPerfil, Atelie
from atelie.models import Produto, Servico


class CadastroClienteForm(UserCreationForm):
    """Form para cadastro de cliente."""
    
    nome_completo = forms.CharField(max_length=200, label='Nome Completo')
    telefone = forms.CharField(max_length=11, label='Telefone', help_text='DDD + 9 dígitos')
    
    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_cliente = True
        if commit:
            user.save()
            # Criar perfil
            PessoaPerfil.objects.create(
                user=user,
                nome_completo=self.cleaned_data['nome_completo'],
                telefone=self.cleaned_data['telefone']
            )
        return user


class CadastroAtelieForm(UserCreationForm):
    """Form para cadastro de ateliê."""
    
    nome_completo = forms.CharField(max_length=200, label='Nome Completo do Responsável')
    telefone = forms.CharField(max_length=11, label='Telefone Pessoal', help_text='DDD + 9 dígitos')
    nome_fantasia = forms.CharField(max_length=200, label='Nome do Ateliê')
    especialidades = forms.CharField(widget=forms.Textarea, label='Especialidades')
    telefone_comercial = forms.CharField(max_length=11, label='Telefone Comercial')
    endereco = forms.CharField(max_length=300, label='Endereço')
    cnpj = forms.CharField(max_length=14, required=False, label='CNPJ (opcional)')
    
    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_atelie = True
        if commit:
            user.save()
            # Criar perfil
            PessoaPerfil.objects.create(
                user=user,
                nome_completo=self.cleaned_data['nome_completo'],
                telefone=self.cleaned_data['telefone']
            )
            # Criar ateliê
            Atelie.objects.create(
                user=user,
                nome_fantasia=self.cleaned_data['nome_fantasia'],
                especialidades=self.cleaned_data['especialidades'],
                telefone_comercial=self.cleaned_data['telefone_comercial'],
                endereco=self.cleaned_data['endereco'],
                cnpj=self.cleaned_data.get('cnpj', '')
            )
        return user


class PerfilForm(forms.ModelForm):
    """Form para edição de perfil."""
    
    class Meta:
        model = PessoaPerfil
        fields = ['nome_completo', 'telefone', 'endereco', 'cidade', 'uf', 'cep']


class AtelieForm(forms.ModelForm):
    """Form para edição de ateliê."""
    
    class Meta:
        model = Atelie
        fields = [
            'nome_fantasia', 'especialidades', 'cnpj',
            'telefone_comercial', 'endereco',
            'geolocalizacao_lat', 'geolocalizacao_lng'
        ]


class PedidoClienteForm(forms.Form):
    """Formulario para criacao de pedidos pelos clientes."""

    atelie = forms.ModelChoiceField(
        queryset=Atelie.objects.filter(ativo=True),
        label='Escolha o Atelie'
    )
    produtos = forms.ModelMultipleChoiceField(
        queryset=Produto.objects.filter(ativo=True),
        required=False,
        label='Produtos',
        widget=forms.CheckboxSelectMultiple
    )
    servicos = forms.ModelMultipleChoiceField(
        queryset=Servico.objects.filter(ativo=True),
        required=False,
        label='Servicos',
        widget=forms.CheckboxSelectMultiple
    )
    data_agendada = forms.DateField(
        label='Data do Agendamento',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    hora_agendada = forms.TimeField(
        label='Horario',
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    observacoes = forms.CharField(
        label='Observacoes',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )

    def clean(self):
        cleaned = super().clean()
        produtos = cleaned.get('produtos')
        servicos = cleaned.get('servicos')
        if not produtos and not servicos:
            raise forms.ValidationError('Selecione ao menos um produto ou servico.')
        if not cleaned.get('data_agendada') or not cleaned.get('hora_agendada'):
            raise forms.ValidationError('Informe data e horario do agendamento.')
        return cleaned
