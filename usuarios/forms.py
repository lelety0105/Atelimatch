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
    telefone = forms.CharField(
        max_length=11,
        label='Telefone',
        help_text='DDD + 9 digitos'
    )
    cep = forms.CharField(
        max_length=8,
        label='CEP',
        help_text='Apenas numeros',
        required=False
    )
    rua = forms.CharField(max_length=300, label='Rua', required=False)
    numero = forms.CharField(max_length=10, label='Numero', required=False)
    complemento = forms.CharField(
        max_length=200,
        label='Complemento (opcional)',
        required=False
    )
    bairro = forms.CharField(max_length=100, label='Bairro', required=False)
    cidade = forms.CharField(max_length=100, label='Cidade', required=False)
    uf = forms.CharField(
        max_length=2,
        label='UF',
        help_text='Ex: SP, RJ, MG',
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_cliente = True
        if commit:
            user.save()
            PessoaPerfil.objects.create(
                user=user,
                nome_completo=self.cleaned_data['nome_completo'],
                telefone=self.cleaned_data['telefone'],
                cep=self.cleaned_data.get('cep', ''),
                rua=self.cleaned_data.get('rua', ''),
                numero=self.cleaned_data.get('numero', ''),
                complemento=self.cleaned_data.get('complemento', ''),
                bairro=self.cleaned_data.get('bairro', ''),
                cidade=self.cleaned_data.get('cidade', ''),
                uf=self.cleaned_data.get('uf', ''),
                endereco=f"{self.cleaned_data.get('rua', '')}, {self.cleaned_data.get('numero', '')}".strip(', ')
            )
        return user

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if PessoaPerfil.objects.filter(telefone=telefone).exists():
            raise forms.ValidationError('Este número de telefone já está em uso. Por favor, insira outro número.')
        return telefone


class CadastroAtelieForm(UserCreationForm):
    """Form para cadastro de atelie."""

    nome_completo = forms.CharField(max_length=200, label='Nome Completo do Responsavel')
    telefone = forms.CharField(
        max_length=11,
        label='Telefone Pessoal',
        help_text='DDD + 9 digitos'
    )
    nome_fantasia = forms.CharField(max_length=200, label='Nome do Atelie')
    especialidades = forms.CharField(widget=forms.Textarea, label='Especialidades')
    telefone_comercial = forms.CharField(max_length=11, label='Telefone Comercial')
    cep = forms.CharField(
        max_length=8,
        label='CEP',
        help_text='Apenas numeros'
    )
    rua = forms.CharField(max_length=300, label='Rua')
    numero = forms.CharField(max_length=10, label='Numero')
    complemento = forms.CharField(
        max_length=200,
        label='Complemento (opcional)',
        required=False
    )
    bairro = forms.CharField(max_length=100, label='Bairro')
    cidade = forms.CharField(max_length=100, label='Cidade')
    uf = forms.CharField(
        max_length=2,
        label='UF',
        help_text='Ex: SP, RJ, MG'
    )
    cnpj = forms.CharField(
        max_length=14,
        required=False,
        label='CNPJ (opcional)'
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_atelie = True
        if commit:
            user.save()
            PessoaPerfil.objects.create(
                user=user,
                nome_completo=self.cleaned_data['nome_completo'],
                telefone=self.cleaned_data['telefone']
            )
            Atelie.objects.create(
                user=user,
                nome_fantasia=self.cleaned_data['nome_fantasia'],
                especialidades=self.cleaned_data['especialidades'],
                telefone_comercial=self.cleaned_data['telefone_comercial'],
                cep=self.cleaned_data['cep'],
                rua=self.cleaned_data['rua'],
                numero=self.cleaned_data['numero'],
                complemento=self.cleaned_data.get('complemento', ''),
                bairro=self.cleaned_data['bairro'],
                cidade=self.cleaned_data['cidade'],
                uf=self.cleaned_data['uf'],
                cnpj=self.cleaned_data.get('cnpj', '')
            )
        return user


class PerfilForm(forms.ModelForm):
    """Form para edicao de perfil."""

    class Meta:
        model = PessoaPerfil
        fields = [
            'nome_completo',
            'telefone',
            'cep',
            'rua',
            'numero',
            'complemento',
            'bairro',
            'cidade',
            'uf',
        ]


class AtelieForm(forms.ModelForm):
    """Form para edicao de atelie."""

    class Meta:
        model = Atelie
        fields = [
            'nome_fantasia', 'especialidades', 'cnpj',
            'telefone_comercial', 'cep', 'rua', 'numero',
            'complemento', 'bairro', 'cidade', 'uf',
            'geolocalizacao_lat', 'geolocalizacao_lng'
        ]


class PedidoClienteForm(forms.Form):
    """Formulario para criacao de pedidos pelos clientes."""

    atelie = forms.ModelChoiceField(
        queryset=Atelie.objects.filter(ativo=True),
        label='Escolha o Atelie'
    )
    produto = forms.ModelChoiceField(queryset=Produto.objects.none(), required=False, label='Produto')
    servico = forms.ModelChoiceField(queryset=Servico.objects.none(), required=False, label='Servico')
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

    def __init__(self, *args, **kwargs):
        atelie = kwargs.pop('atelie', None)
        super().__init__(*args, **kwargs)

        atelie_id = None
        if atelie is not None:
            atelie_id = atelie.id
        elif 'atelie' in self.data:
            try:
                atelie_id = int(self.data.get('atelie'))
            except (TypeError, ValueError):
                atelie_id = None
        elif self.initial.get('atelie'):
            atelie_id = getattr(self.initial['atelie'], 'id', None)

        qs_prod = Produto.objects.filter(ativo=True)
        qs_serv = Servico.objects.filter(ativo=True)
        if atelie_id:
            qs_prod = qs_prod.filter(atelie_id=atelie_id)
            qs_serv = qs_serv.filter(atelie_id=atelie_id)

        self.fields['produto'].queryset = qs_prod
        self.fields['servico'].queryset = qs_serv

    def clean(self):
        cleaned = super().clean()
        produto = cleaned.get('produto')
        servico = cleaned.get('servico')
        if not produto and not servico:
            raise forms.ValidationError('Selecione ao menos um produto ou servico.')
        if not cleaned.get('data_agendada') or not cleaned.get('hora_agendada'):
            raise forms.ValidationError('Informe data e horario do agendamento.')
        return cleaned
