"""
Testes para pedidos e cálculo de valor total.
"""

from django.test import TestCase
from decimal import Decimal
from datetime import date, time
from usuarios.models import CustomUser, Atelie, PessoaPerfil
from atelie.models import Produto, Pedido, ItemPedido, Servico


class PedidoTestCase(TestCase):
    """Testes para o modelo Pedido."""
    
    def setUp(self):
        """Configuração inicial dos testes."""
        # Criar usuário cliente
        self.cliente = CustomUser.objects.create_user(
            email='cliente@test.com',
            password='testpass123',
            is_cliente=True
        )
        PessoaPerfil.objects.create(
            user=self.cliente,
            nome_completo='Cliente Teste',
            telefone='11987654321'
        )
        
        # Criar usuário ateliê
        self.atelie_user = CustomUser.objects.create_user(
            email='atelie@test.com',
            password='testpass123',
            is_atelie=True
        )
        PessoaPerfil.objects.create(
            user=self.atelie_user,
            nome_completo='Ateliê Teste',
            telefone='11987654322'
        )
        self.atelie = Atelie.objects.create(
            user=self.atelie_user,
            nome_fantasia='Ateliê Teste',
            especialidades='Vestidos e saias',
            telefone_comercial='11987654322',
            endereco='Rua Teste, 123'
        )
        
        # Criar produtos e servico
        self.produto1 = Produto.objects.create(
            nome='Vestido',
            categoria='VESTIDO',
            preco_base=Decimal('150.00')
        )
        self.produto2 = Produto.objects.create(
            nome='Saia',
            categoria='SAIA',
            preco_base=Decimal('80.00')
        )
        self.servico = Servico.objects.create(
            nome='Ajuste barra',
            descricao='Ajuste padrao',
            preco_base=Decimal('50.00'),
            ativo=True
        )
        self.data_agendada = date.today()
        self.hora_agendada = time(hour=10, minute=0)
    
    def test_calcular_valor_total_pedido(self):
        """Testa cálculo automático do valor total do pedido."""
        # Criar pedido
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            atelie=self.atelie,
            status='CRIADO',
            data_agendada=self.data_agendada,
            hora_agendada=self.hora_agendada,
        )
        
        # Adicionar itens
        ItemPedido.objects.create(
            pedido=pedido,
            produto=self.produto1,
            qtde=2,
            preco_unitario=self.produto1.preco_base
        )
        ItemPedido.objects.create(
            pedido=pedido,
            produto=self.produto2,
            qtde=1,
            preco_unitario=self.produto2.preco_base
        )
        
        # Calcular valor total
        pedido.calcular_valor_total()
        
        # Verificar cálculo: (150 * 2) + (80 * 1) = 380
        self.assertEqual(pedido.valor_total, Decimal('380.00'))
    
    def test_atualizar_valor_total_ao_adicionar_item(self):
        """Testa atualização automática do valor total ao adicionar item."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            atelie=self.atelie,
            status='CRIADO',
            data_agendada=self.data_agendada,
            hora_agendada=self.hora_agendada,
        )
        
        # Adicionar primeiro item (signal deve atualizar valor_total)
        ItemPedido.objects.create(
            pedido=pedido,
            produto=self.produto1,
            qtde=1,
            preco_unitario=self.produto1.preco_base
        )
        
        # Recarregar pedido do banco
        pedido.refresh_from_db()
        
        # Verificar valor total
        self.assertEqual(pedido.valor_total, Decimal('150.00'))
    
    def test_atualizar_valor_total_ao_remover_item(self):
        """Testa atualização automática do valor total ao remover item."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            atelie=self.atelie,
            status='CRIADO',
            data_agendada=self.data_agendada,
            hora_agendada=self.hora_agendada,
        )
        
        item1 = ItemPedido.objects.create(
            pedido=pedido,
            produto=self.produto1,
            qtde=1,
            preco_unitario=self.produto1.preco_base
        )
        item2 = ItemPedido.objects.create(
            pedido=pedido,
            produto=self.produto2,
            qtde=1,
            preco_unitario=self.produto2.preco_base
        )
        
        # Remover um item
        item1.delete()
        
        # Recarregar pedido do banco
        pedido.refresh_from_db()
        
        # Verificar valor total (deve ser apenas do produto2)
        self.assertEqual(pedido.valor_total, Decimal('80.00'))

    def test_criar_item_servico(self):
        """Garante que servicos tambem entram no pedido."""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            atelie=self.atelie,
            status='CRIADO',
            data_agendada=self.data_agendada,
            hora_agendada=self.hora_agendada,
        )
        ItemPedido.objects.create(
            pedido=pedido,
            servico=self.servico,
            qtde=1,
            preco_unitario=self.servico.preco_base
        )
        pedido.refresh_from_db()
        self.assertEqual(pedido.valor_total, Decimal('50.00'))
        item = pedido.itens.first()
        self.assertEqual(item.descricao_item, 'Ajuste barra')
