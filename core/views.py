"""
Views do core (páginas de erro).
"""

from django.shortcuts import render


def error_404(request, exception):
    """Página de erro 404."""
    return render(request, '404.html', status=404)


def error_500(request):
    """Página de erro 500."""
    return render(request, '500.html', status=500)
