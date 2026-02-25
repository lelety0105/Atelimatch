"""
Modelos do app atelie.
"""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Produto(models.Model):
    """
    Modelo de Produto.
    """

    CATEGORIAS = [
        ("VESTIDO", "Vestido"),
        ("SAIA", "Saia"),
        ("BLUSA", "Blusa"),
        ("CALCA", "Calca"),
        ("CONJUNTO", "Conjunto"),
        ("ACESSORIO", "Acessorio"),
        ("OUTRO", "Outro"),
    ]

    atelie = models.ForeignKey(
        "usuarios.Atelie",
        on_delete=models.CASCADE,
        related_name="produtos",
        verbose_name="Atelie",
        blank=True,
        null=True,
    )
    nome = models.CharField("Nome", max_length=200)
    categoria = models.CharField("Categoria", max_length=20, choices=CATEGORIAS)
    preco_base = models.DecimalField(
        "Preco Base",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    descricao = models.TextField("Descricao", blank=True)
    ativo = models.BooleanField("Ativo", default=True)

    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["-criado_em"]

    def __str__(self) -> str:
        return f"{self.nome} - R$ {self.preco_base}"


class Servico(models.Model):
    """
    Modelo de Servico oferecido pelo atelie.
    """

    atelie = models.ForeignKey(
        "usuarios.Atelie",
        on_delete=models.CASCADE,
        related_name="servicos",
        verbose_name="Atelie",
        blank=True,
        null=True,
    )
    nome = models.CharField("Nome", max_length=200)
    descricao = models.TextField("Descricao", blank=True)
    preco_base = models.DecimalField(
        "Preco Base",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    duracao_estimada = models.IntegerField(
        "Duracao Estimada (minutos)",
        blank=True,
        null=True,
        help_text="Informe em minutos (opcional)",
    )
    ativo = models.BooleanField("Ativo", default=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Servico"
        verbose_name_plural = "Servicos"
        ordering = ["-criado_em"]

    def __str__(self) -> str:
        return f"{self.nome} - R$ {self.preco_base}"


class EstoqueItem(models.Model):
    """
    Modelo de Item de Estoque.
    """

    produto = models.OneToOneField(
        Produto,
        on_delete=models.CASCADE,
        related_name="estoque",
        verbose_name="Produto",
    )
    quantidade_atual = models.IntegerField(
        "Quantidade Atual",
        default=0,
        validators=[MinValueValidator(0)],
    )
    ponto_reposicao = models.IntegerField(
        "Ponto de Reposicao",
        default=5,
        validators=[MinValueValidator(0)],
        help_text="Quantidade minima antes de alertar sobre reposicao",
    )

    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Item de Estoque"
        verbose_name_plural = "Itens de Estoque"

    def __str__(self) -> str:
        return f"{self.produto.nome} - Qtd: {self.quantidade_atual}"

    @property
    def precisa_reposicao(self) -> bool:
        """Verifica se o item precisa de reposicao."""
        return self.quantidade_atual <= self.ponto_reposicao


class Pedido(models.Model):
    """
    Modelo de Pedido.
    """

    STATUS_CHOICES = [
        ("AGUARDANDO_ORCAMENTO", "Aguardando orcamento"),
        ("AGUARDANDO_APROVACAO", "Aguardando aprovacao"),
        ("ORCAMENTO_REPROVADO", "Orcamento reprovado"),
        ("AGUARDANDO_PAGAMENTO", "Aguardando pagamento"),
        ("EM_ANDAMENTO", "Em andamento"),
        ("AGUARDANDO_RETIRADA", "Aguardando retirada"),
        ("FINALIZADO", "Finalizado"),
        ("CANCELADO", "Cancelado"),
    ]

    TIPO_SERVICO_CHOICES = [
        ("CRIANCAO", "Criacao de look / peca"),
        ("AJUSTES", "Ajustes"),
        ("OUTROS", "Outros"),
    ]

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pedidos_cliente",
        verbose_name="Cliente",
        limit_choices_to={"is_cliente": True},
    )
    atelie = models.ForeignKey(
        "usuarios.Atelie",
        on_delete=models.PROTECT,
        related_name="pedidos",
        verbose_name="Atelie",
    )
    tipo_servico = models.CharField(
        "Tipo de servico",
        max_length=20,
        choices=TIPO_SERVICO_CHOICES,
        default="OUTROS",
    )
    descricao_cliente = models.TextField(
        "Descricao do pedido (cliente)",
        blank=True,
    )
    status = models.CharField(
        "Status",
        max_length=30,
        choices=STATUS_CHOICES,
        default="AGUARDANDO_ORCAMENTO",
    )
    valor_total = models.DecimalField(
        "Valor Total",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    valor_orcado = models.DecimalField(
        "Valor orcado",
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    prazo_entrega = models.DateField(
        "Prazo de entrega",
        blank=True,
        null=True,
    )
    observacoes = models.TextField("Observacoes", blank=True)
    data_agendada = models.DateField(
        "Data do agendamento",
        blank=True,
        null=True,
    )
    hora_agendada = models.TimeField(
        "Hora do agendamento",
        blank=True,
        null=True,
    )

    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-criado_em"]

    def __str__(self) -> str:
        return f"Pedido #{self.pk} - {self.cliente.email} - {self.status}"

    def calcular_valor_total(self) -> Decimal:
        """Calcula o valor total do pedido baseado nos itens."""
        total = sum(item.subtotal for item in self.itens.all())
        self.valor_total = total
        self.save(update_fields=["valor_total"])
        return total

    @property
    def agendamento_formatado(self) -> str:
        """Retorna a data/hora de agendamento formatada."""
        if self.data_agendada and self.hora_agendada:
            return f"{self.data_agendada.strftime('%d/%m/%Y')} as {self.hora_agendada.strftime('%H:%M')}"
        if self.data_agendada:
            return self.data_agendada.strftime("%d/%m/%Y")
        return "Nao agendado"

    @property
    def resumo_servico(self) -> str:
        """Retorna um resumo simples dos itens do pedido."""
        primeiro = self.itens.select_related("produto", "servico").first()
        if primeiro:
            return primeiro.descricao_item
        return "Itens do pedido"


class ItemPedido(models.Model):
    """
    Modelo de Item de Pedido.
    """

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Pedido",
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name="itens_pedido",
        verbose_name="Produto",
        blank=True,
        null=True,
    )
    servico = models.ForeignKey(
        "atelie.Servico",
        on_delete=models.PROTECT,
        related_name="itens_servico",
        verbose_name="Servico",
        blank=True,
        null=True,
    )
    qtde = models.IntegerField(
        "Quantidade",
        validators=[MinValueValidator(1)],
    )
    preco_unitario = models.DecimalField(
        "Preco unitario",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    criado_em = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Item de Pedido"
        verbose_name_plural = "Itens de Pedido"

    def __str__(self) -> str:
        return f"{self.descricao_item} x{self.qtde}"

    @property
    def subtotal(self) -> Decimal:
        """Calcula o subtotal do item."""
        return self.preco_unitario * self.qtde

    @property
    def descricao_item(self) -> str:
        if self.produto:
            return self.produto.nome
        if self.servico:
            return self.servico.nome
        return "Item"


class ChatMensagem(models.Model):
    """
    Mensagens trocadas entre cliente e atelie por pedido.
    """

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="mensagens",
        verbose_name="Pedido",
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mensagens",
        verbose_name="Autor",
    )
    conteudo = models.TextField("Mensagem")
    lida_por_cliente = models.BooleanField("Lida pelo cliente", default=False)
    lida_por_atelie = models.BooleanField("Lida pelo atelie", default=False)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Mensagem de Chat"
        verbose_name_plural = "Mensagens de Chat"
        ordering = ["-criado_em"]

    def marcar_como_lida(self, usuario) -> None:
        """Marca a mensagem como lida para o perfil informado."""
        if getattr(usuario, "is_cliente", False) and not self.lida_por_cliente:
            self.lida_por_cliente = True
            self.save(update_fields=["lida_por_cliente"])
        elif getattr(usuario, "is_atelie", False) and not self.lida_por_atelie:
            self.lida_por_atelie = True
            self.save(update_fields=["lida_por_atelie"])
