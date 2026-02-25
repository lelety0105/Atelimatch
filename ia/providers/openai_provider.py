"""
Provider de geração de imagens usando OpenAI DALL-E.
"""

from typing import Dict
from django.conf import settings
from .base import BaseImageProvider


class OpenAIImageProvider(BaseImageProvider):
    """
    Provider para geração de imagens usando OpenAI DALL-E.
    """
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY não configurada. "
                "Por favor, configure a variável de ambiente OPENAI_API_KEY."
            )
    
    def generate_image(
        self,
        prompt: str,
        size: str = "512x512",
        **kwargs
    ) -> Dict[str, any]:
        """
        Gera uma imagem usando DALL-E.
        """
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            
            # Mapear tamanhos para DALL-E 3
            size_map = {
                "512x512": "1024x1024",  # DALL-E 3 não suporta 512x512
                "1024x1024": "1024x1024",
                "1792x1024": "1792x1024",
                "1024x1792": "1024x1792",
            }
            
            dalle_size = size_map.get(size, "1024x1024")
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=dalle_size,
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            
            return {
                'success': True,
                'url': image_url,
                'error': None,
                'metadata': {
                    'model': 'dall-e-3',
                    'size': dalle_size,
                    'revised_prompt': getattr(response.data[0], 'revised_prompt', None),
                }
            }
        
        except ImportError:
            return {
                'success': False,
                'url': None,
                'error': 'Biblioteca openai não instalada. Execute: pip install openai',
                'metadata': {}
            }
        
        except Exception as e:
            return {
                'success': False,
                'url': None,
                'error': f'Erro ao gerar imagem: {str(e)}',
                'metadata': {}
            }
    
    def get_provider_name(self) -> str:
        """Retorna o nome do provedor."""
        return "OpenAI DALL-E"
