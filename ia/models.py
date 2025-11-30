"""
Modelos do app ia (Inteligência Artificial).
"""

from django.db import models
from django.conf import settings


class PromptImagem(models.Model):
    """
    Modelo para armazenar prompts e imagens geradas pela IA.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prompts_imagem',
        verbose_name='Usuário'
    )
    prompt = models.TextField('Prompt', help_text='Descrição do look/peça desejada')
    
    # Armazenamento da imagem gerada
    arquivo = models.ImageField(
        'Arquivo',
        upload_to='gerados/%Y/%m/%d/',
        blank=True,
        null=True
    )
    url_arquivo = models.URLField('URL do Arquivo', blank=True, null=True)
    
    # Metadados da geração
    modelo = models.CharField(
        'Modelo de IA',
        max_length=100,
        default='dall-e-3',
        help_text='Modelo de IA utilizado para gerar a imagem'
    )
    parametros_json = models.JSONField(
        'Parâmetros',
        default=dict,
        blank=True,
        help_text='Parâmetros adicionais da geração (tamanho, estilo, etc.)'
    )
    
    # Status da geração
    sucesso = models.BooleanField('Sucesso', default=True)
    mensagem_erro = models.TextField('Mensagem de Erro', blank=True)
    
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Prompt de Imagem'
        verbose_name_plural = 'Prompts de Imagens'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f'{self.usuario.email} - {self.prompt[:50]}...'

    @property
    def imagem_url(self) -> str:
        """
        Retorna a URL da imagem para exibi��ǜo priorizando o arquivo salvo
        localmente. Caso o arquivo nǜo esteja dispon��vel, utiliza a URL remota.
        """
        if self.arquivo:
            try:
                return self.arquivo.url
            except ValueError:
                # Campo configurado mas arquivo nǜo existe no disco
                pass
        return self.url_arquivo or ''
