from django.apps import AppConfig


class AtelieConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'atelie'
    verbose_name = 'Ateliê'
    
    def ready(self):
        """Importa os signals quando o app estiver pronto."""
        import atelie.signals
