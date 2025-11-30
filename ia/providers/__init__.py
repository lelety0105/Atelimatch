"""
Módulo de provedores de IA para geração de imagens.
"""

from django.conf import settings
from .base import BaseImageProvider
from .openai_provider import OpenAIImageProvider


def get_image_provider() -> BaseImageProvider:
    """
    Factory function para obter o provedor de imagens configurado.
    
    Returns:
        Instância do provedor de imagens configurado.
    
    Raises:
        ValueError: Se o provedor não estiver configurado ou for inválido.
    """
    provider_name = settings.AI_PROVIDER.lower()
    
    if provider_name == 'openai':
        return OpenAIImageProvider()
    else:
        raise ValueError(
            f"Provedor '{provider_name}' não suportado. "
            f"Provedores disponíveis: openai"
        )


__all__ = ['BaseImageProvider', 'OpenAIImageProvider', 'get_image_provider']
