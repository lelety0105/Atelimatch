"""
Modelos do app atelie.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class Produto(models.Model):
    """
    Modelo de Produto.
    """
    CATEGORIAS = [
        ('VESTIDO', 'Vestido'),
        ('SAIA', 'Saia'),
        ('BLUSA', 'Blusa'),
        ('CALCA', 'Calça'),
        ('CONJUNTO', 'Conjunto'),
        ('ACESSORIO', 'Acessório'),
        ('OUTRO', 'Outro'),
    ]
    
    nome = models.CharField('Nome', max_length=200)
    categoria = models.CharField('Categoria', max_length=20, choices=CATEGORIAS)
    preco_base = models.DecimalField(
        'Preço Base',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f'{self.nome} - R$ {self.preco_base}'


class Servico(models.Model):
    """
    Modelo de Serviço oferecido pelo ateliê.
    """
    nome = models.CharField('Nome', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    preco_base = models.DecimalField(
        'Preço Base',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    duracao_estimada = models.IntegerField(
        'Duração Estimada (minutos)',
        blank=True,
        null=True,
        help_text='Informe em minutos (opcional)'
    )
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.nome} - R$ {self.preco_base}'


class EstoqueItem(models.Model):
    """
    Modelo de Item de Estoque.
    """
    produto = models.OneToOneField(
        Produto,
        on_delete=models.CASCADE,
        related_name='estoque',
        verbose_name='Produto'
    )
    quantidade_atual = models.IntegerField(
        'Quantidade Atual',
        default=0,
        validators=[MinValueValidator(0)]
    )
    ponto_reposicao = models.IntegerField(
        'Ponto de Reposição',
        default=5,
        validators=[MinValueValidator(0)],
        help_text='Quantidade mínima antes de alertar sobre reposição'
    )
    
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Item de Estoque'
        verbose_name_plural = 'Itens de Estoque'
    
    def __str__(self):
        return f'{self.produto.nome} - Qtd: {self.quantidade_atual}'
    
    @property
    def precisa_reposicao(self):
        """Verifica se o item precisa de reposição."""
        return self.quantidade_atual <= self.ponto_reposicao


class Pedido(models.Model):
    """
    Modelo de Pedido.
    """
    STATUS_CHOICES = [
        ('AGUARDANDO_ORCAMENTO', 'Aguardando Orçamento'),
        ('AGUARDANDO_APROVACAO', 'Aguardando Aprovação'),
        ('ORCAMENTO_REPROVADO', 'Orçamento Reprovado'),
        ('AGUARDANDO_PAGAMENTO', 'Aguardando Pagamento'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('AGUARDANDO_RETIRADA', 'Aguardando Retirada'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]
    TIPO_SERVICO_CHOICES = [
        ('CRIANCAO', 'Criação de look / peça'),
        ('AJUSTES', 'Ajustes'),
        ('OUTROS', 'Outros'),
    ]
    
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='pedidos_cliente',
        verbose_name='Cliente',
        limit_choices_to={'is_cliente': True}
    )
    atelie = models.ForeignKey(
        'usuarios.Atelie',
        on_delete=models.PROTECT,
        related_name='pedidos',
        verbose_name='Ateliê'
    )
    tipo_servico = models.CharField(
        'Tipo de Serviço',
        max_length=20,
        choices=TIPO_SERVICO_CHOICES,
        default='OUTROS'
    )
    status = models.CharField(
        'Status',
        max_length=20,
        choices=STATUS_CHOICES,
        default='AGUARDANDO_ORCAMENTO'
    )
    valor_total = models.DecimalField(
        'Valor Total',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    observacoes = models.TextField('Observações', blank=True)
    data_agendada = models.DateField(
        'Data do Agendamento',
        blank=True,
        null=True
    )
    hora_agendada = models.TimeField(
        'Hora do Agendamento',
        blank=True,
        null=True
    )
    
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f'Pedido #{self.pk} - {self.cliente.email} - {self.status}'
    
    def calcular_valor_total(self):
        """Calcula o valor total do pedido baseado nos itens."""
        total = sum(item.subtotal for item in self.itens.all())
        self.valor_total = total
        self.save()
        return total

    @property
    def agendamento_formatado(self):
        """Retorna a data/hora de agendamento formatada."""
        if self.data_agendada and self.hora_agendada:
            return f'{self.data_agendada.strftime("%d/%m/%Y")} às {self.hora_agendada.strftime("%H:%M")}'
        if self.data_agendada:
            return self.data_agendada.strftime("%d/%m/%Y")
        return 'Não agendado'

    @property
    def resumo_servico(self):
        """Retorna um resumo simples dos itens do pedido."""
        primeiro = self.itens.select_related('produto', 'servico').first()
        if primeiro:
            return primeiro.descricao_item
        return 'Itens do pedido'


class ItemPedido(models.Model):
    """
    Modelo de Item de Pedido.
    """
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Pedido'
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='itens_pedido',
        verbose_name='Produto',
        blank=True,
        null=True
    )
    servico = models.ForeignKey(
        'atelie.Servico',
        on_delete=models.PROTECT,
        related_name='itens_servico',
        verbose_name='Serviço',
        blank=True,
        null=True
    )
    qtde = models.IntegerField(
        'Quantidade',
        validators=[MinValueValidator(1)]
    )
    preco_unitario = models.DecimalField(
        'Preço Unitário',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Itens de Pedido'
    
    def __str__(self):
        return f'{self.descricao_item} x{self.qtde}'
    
    @property
    def subtotal(self):
        """Calcula o subtotal do item."""
        return self.preco_unitario * self.qtde

    @property
    def descricao_item(self):
        if self.produto:
            return self.produto.nome
        if self.servico:
            return self.servico.nome
        return 'Item'


class ChatMensagem(models.Model):
    """
    Mensagens trocadas entre cliente e ateliê por pedido.
    """
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='mensagens',
        verbose_name='Pedido'
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mensagens',
        verbose_name='Autor'
    )
    conteudo = models.TextField('Mensagem')
    lida_por_cliente = models.BooleanField('Lida pelo cliente', default=False)
    lida_por_atelie = models.BooleanField('Lida pelo ateliê', default=False)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Mensagem de Chat'
        verbose_name_plural = 'Mensagens de Chat'
        ordering = ['-criado_em']

    def marcar_como_lida(self, usuario):
        """Marca a mensagem como lida para o perfil informado."""
        if usuario.is_cliente and not self.lida_por_cliente:
            self.lida_por_cliente = True
            self.save(update_fields=['lida_por_cliente'])
        elif usuario.is_atelie and not self.lida_por_atelie:
            self.lida_por_atelie = True
            self.save(update_fields=['lida_por_atelie'])
