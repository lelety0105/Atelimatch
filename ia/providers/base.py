"""
Interface base para provedores de IA de geração de imagens.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class BaseImageProvider(ABC):
    """
    Classe base abstrata para provedores de geração de imagens.
    """
    
    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        size: str = "512x512",
        **kwargs
    ) -> Dict[str, any]:
        """
        Gera uma imagem a partir de um prompt.
        
        Args:
            prompt: Descrição textual da imagem desejada
            size: Tamanho da imagem (ex: "512x512", "1024x1024")
            **kwargs: Parâmetros adicionais específicos do provedor
        
        Returns:
            Dict contendo:
                - success: bool indicando sucesso
                - url: URL da imagem gerada (se sucesso)
                - error: Mensagem de erro (se falha)
                - metadata: Metadados adicionais
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Retorna o nome do provedor.
        """
        pass
