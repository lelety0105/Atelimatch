
import os
import requests
from django.conf import settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

class Misconfigured(Exception):
    pass

def _get_api_key():
    # Usa variável de ambiente OPENROUTER_API_KEY ou settings
    key = os.getenv("OPENROUTER_API_KEY") or getattr(settings, "OPENROUTER_API_KEY", None)
    if not key:
        raise Misconfigured("Defina OPENROUTER_API_KEY no ambiente ou settings.py.")
    return key

def generate_completion(system: str, user: str) -> str:
    api_key = _get_api_key()
    # Modelo free–tier sugerido (DeepSeek R1/Chat gratuito costuma estar disponível no OpenRouter).
    # Você pode trocar por outro disponível no plano gratuito: veja a página de modelos free do OpenRouter.
    model = getattr(settings, "IA_MODEL", "deepseek/deepseek-r1:free")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://Atelimatch.local",  # opcional
        "X-Title": "AteliêHub Ideias",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.7,
        "max_tokens": 600,
    }
    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        j = resp.json()
        try:
            return j["choices"][0]["message"]["content"]
        except Exception:
            return "Não recebi uma resposta válida do provedor no momento. Tente novamente."
    except requests.exceptions.Timeout:
        raise Exception("Timeout ao conectar com a IA. Tente novamente.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro ao conectar com a IA: {str(e)}")

