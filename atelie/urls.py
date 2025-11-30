"""
URLs do app `atelie`.
"""

from django.urls import path
from . import views

app_name = "atelie"

urlpatterns = [
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),

    # CRUD Produtos
    path("produtos/", views.produto_list, name="produto_list"),
    path("produtos/novo/", views.produto_create, name="produto_create"),
    path("produtos/<int:pk>/editar/", views.produto_update, name="produto_update"),
    path("produtos/<int:pk>/deletar/", views.produto_delete, name="produto_delete"),

    # CRUD Serviços
    path("servicos/", views.servico_list, name="servico_list"),
    path("servicos/novo/", views.servico_create, name="servico_create"),
    path("servicos/<int:pk>/editar/", views.servico_update, name="servico_update"),
    path("servicos/<int:pk>/deletar/", views.servico_delete, name="servico_delete"),

    # Chats
    path("chats/", views.chats, name="chats"),
    path("pedidos/<int:pk>/chat/", views.pedido_chat, name="pedido_chat"),

    # CRUD Estoque
    path("estoque/", views.estoque_list, name="estoque_list"),
    path("estoque/novo/", views.estoque_create, name="estoque_create"),
    path("estoque/<int:pk>/editar/", views.estoque_update, name="estoque_update"),

    # CRUD Pedidos
    path("pedidos/", views.pedido_list, name="pedido_list"),
    path("pedidos/<int:pk>/", views.pedido_detail, name="pedido_detail"),
    path("pedidos/<int:pk>/editar/", views.pedido_edit_atelie, name="pedido_edit_atelie"),
]
