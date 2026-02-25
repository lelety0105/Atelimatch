import json
import logging
import mimetypes
import os
from uuid import uuid4
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods, require_POST

from . import services
from .models import PromptImagem
from .providers import get_image_provider

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Tu Ǹs um consultor de inova��ǜo para ateliǦs de costura no Brasil. "
    "Gere ideias prǭticas de novos servi��os/produtos, melhorias de processo, "
    "experiǦncias do cliente e parcerias locais. Responda em portuguǦs (PT-BR), "
    "em tom simples, objetivo e com foco em viabilidade."
)


def _infer_extension(image_url: str, content_type: str | None) -> str:
    """Retorna extens��ǜo deduzida a partir da URL ou do Content-Type."""
    parsed = urlparse(image_url)
    _, ext = os.path.splitext(parsed.path)
    if ext:
        return ext
    if content_type:
        guessed = mimetypes.guess_extension(content_type.split(';')[0].strip())
        if guessed:
            return guessed
    return '.png'


def _generate_filename(prompt: str, extension: str) -> str:
    """Gera um nome de arquivo amig��vel baseado no prompt."""
    slug = slugify(prompt) or 'look'
    return f"{slug[:40]}-{uuid4().hex[:8]}{extension}"


def _download_image_to_content(image_url: str, prompt: str) -> tuple[str, ContentFile]:
    """Realiza o download da imagem retornando nome do arquivo e ContentFile."""
    response = requests.get(image_url, timeout=60)
    response.raise_for_status()
    extension = _infer_extension(image_url, response.headers.get('Content-Type'))
    filename = _generate_filename(prompt, extension)
    return filename, ContentFile(response.content)


@login_required
def studio(request):
    """Tela principal do studio de gera��ǜo de looks."""
    historico_qs = PromptImagem.objects.filter(
        usuario=request.user
    ).order_by('-criado_em')
    historico = historico_qs[:20]
    ultima_imagem = historico_qs.filter(sucesso=True).first()

    context = {
        'historico': historico,
        'ultima_imagem': ultima_imagem,
        'default_size': getattr(settings, 'AI_IMAGE_SIZE', '512x512'),
    }
    return render(request, "ia/studio.html", context)


@login_required
@require_POST
def gerar_imagem(request):
    """Endpoint AJAX respons��vel por gerar uma nova imagem."""
    prompt = (request.POST.get('prompt') or '').strip()
    if not prompt:
        return JsonResponse({'success': False, 'error': 'Prompt nǜo pode ser vazio.'}, status=400)

    size = request.POST.get('size') or getattr(settings, 'AI_IMAGE_SIZE', '512x512')
    size = size if size in {'512x512', '1024x1024', '1792x1024', '1024x1792'} else '1024x1024'

    try:
        provider = get_image_provider()
    except Exception as exc:
        logger.exception("IA provider nǜo configurado: %s", exc)
        return JsonResponse({'success': False, 'error': 'Provedor de IA nǜo configurado.'}, status=500)

    try:
        provider_result = provider.generate_image(prompt=prompt, size=size)
    except Exception as exc:
        logger.exception("Erro ao acionar provedor de IA: %s", exc)
        provider_result = {'success': False, 'url': None, 'error': str(exc), 'metadata': {}}

    metadata = provider_result.get('metadata') or {}
    modelo = metadata.get('model') or provider.get_provider_name()
    parametros = {'size': size}
    if metadata:
        parametros['metadata'] = metadata

    prompt_obj = PromptImagem.objects.create(
        usuario=request.user,
        prompt=prompt,
        modelo=modelo,
        parametros_json=parametros,
        sucesso=provider_result.get('success', False),
        mensagem_erro=provider_result.get('error') or '',
    )

    if not provider_result.get('success'):
        error_message = provider_result.get('error') or 'Falha ao gerar a imagem.'
        logger.error("Falha na gera��ǜo de imagem: %s", error_message)
        prompt_obj.mensagem_erro = error_message
        prompt_obj.save(update_fields=['mensagem_erro'])
        return JsonResponse({'success': False, 'error': error_message}, status=502)

    image_url = provider_result.get('url')
    if not image_url:
        error_message = 'O provedor nǜo retornou uma URL de imagem.'
        prompt_obj.sucesso = False
        prompt_obj.mensagem_erro = error_message
        prompt_obj.save(update_fields=['sucesso', 'mensagem_erro'])
        return JsonResponse({'success': False, 'error': error_message}, status=500)

    try:
        filename, content = _download_image_to_content(image_url, prompt)
        prompt_obj.arquivo.save(filename, content, save=False)
        prompt_obj.url_arquivo = image_url
        prompt_obj.save(update_fields=['arquivo', 'url_arquivo'])
    except Exception as exc:
        logger.exception("Erro ao salvar imagem gerada: %s", exc)
        prompt_obj.sucesso = False
        prompt_obj.mensagem_erro = f'Erro ao salvar imagem: {exc}'
        prompt_obj.save(update_fields=['sucesso', 'mensagem_erro'])
        return JsonResponse({'success': False, 'error': 'Falha ao salvar a imagem gerada.'}, status=500)

    return JsonResponse({'success': True})


def chat_page(request):
    """P��gina HTML do chatbot."""
    return render(request, "ia/chat.html", {
        "model_label": getattr(settings, "IA_MODEL_LABEL", "DeepSeek (via OpenRouter)"),
    })


@require_http_methods(["POST"])
def chat_api(request):
    """API que conversa com o agente de texto."""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("JSON invǭlido")
    user_message = (payload.get("message") or "").strip()
    if not user_message:
        return HttpResponseBadRequest("Mensagem vazia")
    try:
        answer = services.generate_completion(
            system=SYSTEM_PROMPT,
            user=user_message,
        )
        return JsonResponse({"ok": True, "answer": answer})
    except services.Misconfigured as e:
        logger.error("IA Misconfigured: %s", e)
        return JsonResponse({"ok": False, "error": str(e)}, status=500)
    except Exception as e:
        logger.error("IA Error: %s", e, exc_info=True)
        return JsonResponse({"ok": False, "error": f"Falha ao consultar a IA: {str(e)}"}, status=502)
