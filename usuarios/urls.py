"""
URLs do app usuarios.
"""

from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cadastro/cliente/', views.cadastro_cliente, name='cadastro_cliente'),
    path('cadastro/atelie/', views.cadastro_atelie, name='cadastro_atelie'),
    path('dashboard/redirect/', views.redirect_dashboard, name='redirect_dashboard'),
    path('dashboard/cliente/', views.cliente_dashboard, name='cliente_dashboard'),
    path('chats/', views.meus_chats, name='meus_chats'),
    path('pedidos/novo/', views.novo_pedido, name='novo_pedido'),
    path('pedidos/<int:pk>/editar/', views.pedido_edit_cliente, name='pedido_edit_cliente'),
    path('api/cep/<str:cep>/', views.api_cep, name='api_cep'),
]
