"""
URLs principais do projeto Atelimatch.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Apps
    path('usuarios/', include('usuarios.urls')),
    path('atelie/', include('atelie.urls')),
    path('ia/', include(('ia.urls', 'ia'), namespace='ia')),
    
    # Páginas públicas
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('sobre/', TemplateView.as_view(template_name='sobre.html'), name='sobre'),
]

# Servir arquivos de media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Páginas de erro customizadas
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
