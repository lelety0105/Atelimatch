"""
Testes de CRUD de produtos.
"""

from django.test import TestCase
from decimal import Decimal
from atelie.models import Produto


class ProdutoTestCase(TestCase):
    """Testes para o modelo Produto."""
    
    def test_criar_produto(self):
        """Testa criação de produto."""
        produto = Produto.objects.create(
            nome='Vestido Floral',
            categoria='VESTIDO',
            preco_base=Decimal('150.00'),
            descricao='Vestido floral midi',
            ativo=True
        )
        
        self.assertEqual(produto.nome, 'Vestido Floral')
        self.assertEqual(produto.categoria, 'VESTIDO')
        self.assertEqual(produto.preco_base, Decimal('150.00'))
        self.assertTrue(produto.ativo)
    
    def test_listar_produtos(self):
        """Testa listagem de produtos."""
        Produto.objects.create(
            nome='Produto 1',
            categoria='SAIA',
            preco_base=Decimal('100.00')
        )
        Produto.objects.create(
            nome='Produto 2',
            categoria='BLUSA',
            preco_base=Decimal('80.00')
        )
        
        produtos = Produto.objects.all()
        self.assertEqual(produtos.count(), 2)
    
    def test_atualizar_produto(self):
        """Testa atualização de produto."""
        produto = Produto.objects.create(
            nome='Produto Original',
            categoria='SAIA',
            preco_base=Decimal('100.00')
        )
        
        produto.nome = 'Produto Atualizado'
        produto.preco_base = Decimal('120.00')
        produto.save()
        
        produto_atualizado = Produto.objects.get(pk=produto.pk)
        self.assertEqual(produto_atualizado.nome, 'Produto Atualizado')
        self.assertEqual(produto_atualizado.preco_base, Decimal('120.00'))
    
    def test_deletar_produto(self):
        """Testa exclusão de produto."""
        produto = Produto.objects.create(
            nome='Produto para Deletar',
            categoria='OUTRO',
            preco_base=Decimal('50.00')
        )
        
        produto_id = produto.pk
        produto.delete()
        
        with self.assertRaises(Produto.DoesNotExist):
            Produto.objects.get(pk=produto_id)
