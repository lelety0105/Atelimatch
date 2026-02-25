"""
Testes de autenticação.
"""

import pytest
from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import CustomUser, PessoaPerfil


class AuthTestCase(TestCase):
    """Testes de autenticação e redirecionamento."""
    
    def setUp(self):
        """Configuração inicial dos testes."""
        self.client = Client()
        
        # Criar usuário cliente
        self.cliente_user = CustomUser.objects.create_user(
            email='cliente@test.com',
            password='testpass123',
            is_cliente=True
        )
        PessoaPerfil.objects.create(
            user=self.cliente_user,
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
        from usuarios.models import Atelie
        Atelie.objects.create(
            user=self.atelie_user,
            nome_fantasia='Ateliê Teste',
            especialidades='Vestidos',
            telefone_comercial='11987654322',
            endereco='Rua Teste, 123'
        )
    
    def test_login_com_email_sucesso(self):
        """Testa login com e-mail e senha corretos."""
        response = self.client.post(reverse('usuarios:login'), {
            'email': 'cliente@test.com',
            'password': 'testpass123'
        })
        
        # Deve redirecionar após login bem-sucedido
        self.assertEqual(response.status_code, 302)
        
        # Usuário deve estar autenticado
        user = self.client.session.get('_auth_user_id')
        self.assertIsNotNone(user)
    
    def test_login_email_incorreto(self):
        """Testa login com e-mail incorreto."""
        response = self.client.post(reverse('usuarios:login'), {
            'email': 'errado@test.com',
            'password': 'testpass123'
        })
        
        # Não deve redirecionar
        self.assertEqual(response.status_code, 200)
        
        # Usuário não deve estar autenticado
        user = self.client.session.get('_auth_user_id')
        self.assertIsNone(user)
    
    def test_redirecionamento_cliente(self):
        """Testa redirecionamento para dashboard de cliente."""
        self.client.login(username='cliente@test.com', password='testpass123')
        
        response = self.client.get(reverse('usuarios:redirect_dashboard'))
        
        # Deve redirecionar para dashboard de cliente
        self.assertRedirects(response, reverse('usuarios:cliente_dashboard'))
    
    def test_redirecionamento_atelie(self):
        """Testa redirecionamento para dashboard de ateliê."""
        self.client.login(username='atelie@test.com', password='testpass123')
        
        response = self.client.get(reverse('usuarios:redirect_dashboard'))
        
        # Deve redirecionar para dashboard de ateliê
        self.assertRedirects(response, reverse('atelie:dashboard'))
