"""
Context processors customizados para Atelimatch.
"""

from django.conf import settings


def clarity_context(request):
    """
    Adiciona variáveis do Microsoft Clarity ao contexto dos templates.
    """
    return {
        'CLARITY_ID': settings.CLARITY_ID,
        'debug': settings.DEBUG,
    }
