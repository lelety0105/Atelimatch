"""
Signals do app atelie.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ItemPedido


@receiver(post_save, sender=ItemPedido)
def atualizar_valor_total_ao_salvar(sender, instance, **kwargs):
    """
    Atualiza o valor total do pedido ao salvar um item.
    """
    instance.pedido.calcular_valor_total()


@receiver(post_delete, sender=ItemPedido)
def atualizar_valor_total_ao_deletar(sender, instance, **kwargs):
    """
    Atualiza o valor total do pedido ao deletar um item.
    """
    instance.pedido.calcular_valor_total()
