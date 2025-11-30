"""
Modelos do app usuarios.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    """
    Modelo de usuário customizado com autenticação por e-mail.
    """
    username = None  # Remove o campo username
    email = models.EmailField('E-mail', unique=True)
    is_atelie = models.BooleanField('É Ateliê', default=False)
    is_cliente = models.BooleanField('É Cliente', default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return self.email


class PessoaPerfil(models.Model):
    """
    Perfil de pessoa (1:1 com User).
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuário'
    )
    nome_completo = models.CharField('Nome Completo', max_length=200)
    
    # Validador de telefone brasileiro (DDD + 9 dígitos)
    telefone_validator = RegexValidator(
        regex=r'^\d{2}9\d{8}$',
        message='Telefone deve estar no formato: DDXXXXXXXXX (DDD + 9 dígitos)'
    )
    telefone = models.CharField(
        'Telefone',
        max_length=11,
        unique=True,
        validators=[telefone_validator],
        help_text='Formato: DDXXXXXXXXX (apenas números)'
    )
    
    endereco = models.CharField('Endereço', max_length=300, blank=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True)
    uf = models.CharField('UF', max_length=2, blank=True)
    cep = models.CharField('CEP', max_length=8, blank=True, help_text='Apenas números')
    
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Pessoa'
        verbose_name_plural = 'Perfis de Pessoas'
    
    def __str__(self):
        return f'{self.nome_completo} ({self.user.email})'


class Atelie(models.Model):
    """
    Modelo de Ateliê (1:1 com User quando is_atelie=True).
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='atelie',
        verbose_name='Usuário',
        limit_choices_to={'is_atelie': True}
    )
    nome_fantasia = models.CharField('Nome Fantasia', max_length=200)
    especialidades = models.TextField(
        'Especialidades',
        help_text='Descreva as especialidades do ateliê'
    )
    cnpj = models.CharField('CNPJ', max_length=14, blank=True, null=True)
    
    telefone_validator = RegexValidator(
        regex=r'^\d{2}9\d{8}$',
        message='Telefone deve estar no formato: DDXXXXXXXXX (DDD + 9 dígitos)'
    )
    telefone_comercial = models.CharField(
        'Telefone Comercial',
        max_length=11,
        validators=[telefone_validator]
    )
    
    endereco = models.CharField('Endereço', max_length=300)
    geolocalizacao_lat = models.DecimalField(
        'Latitude',
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )
    geolocalizacao_lng = models.DecimalField(
        'Longitude',
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )
    
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Ateliê'
        verbose_name_plural = 'Ateliês'
    
    def __str__(self):
        return self.nome_fantasia
