"""
Testes para fluxo de chat entre cliente e ateliê.
"""

from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from usuarios.models import CustomUser, PessoaPerfil, Atelie
from atelie.models import Pedido, Produto, ItemPedido, ChatMensagem


class ChatViewTests(TestCase):
    """Cobre listagens e envio de mensagens."""

    def setUp(self):
        self.cliente = CustomUser.objects.create_user(
            email='cliente@test.com',
            password='teste123',
            is_cliente=True,
        )
        PessoaPerfil.objects.create(
            user=self.cliente,
            nome_completo='Cliente',
            telefone='11999999999'
        )
        self.user_atelie = CustomUser.objects.create_user(
            email='atelie@test.com',
            password='teste123',
            is_atelie=True,
        )
        PessoaPerfil.objects.create(
            user=self.user_atelie,
            nome_completo='Atelie',
            telefone='11999999998'
        )
        self.atelie = Atelie.objects.create(
            user=self.user_atelie,
            nome_fantasia='Atelie Teste',
            especialidades='Serviços',
            telefone_comercial='11999999998',
            endereco='Rua A, 123'
        )
        self.produto = Produto.objects.create(
            nome='Vestido',
            categoria='VESTIDO',
            preco_base=Decimal('100.00')
        )
        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            atelie=self.atelie,
            status='CRIADO'
        )
        ItemPedido.objects.create(
            pedido=self.pedido,
            produto=self.produto,
            qtde=1,
            preco_unitario=self.produto.preco_base
        )

    def test_cliente_lista_chats(self):
        ChatMensagem.objects.create(
            pedido=self.pedido,
            autor=self.user_atelie,
            conteudo='Olá',
            lida_por_atelie=True
        )
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse('usuarios:meus_chats'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, f'Pedido #{self.pedido.id}')

    def test_cliente_envia_mensagem(self):
        self.client.force_login(self.cliente)
        resp = self.client.post(
            reverse('atelie:pedido_chat', args=[self.pedido.id]),
            {'mensagem': 'Preciso de ajustes'}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(ChatMensagem.objects.filter(pedido=self.pedido).count(), 1)
