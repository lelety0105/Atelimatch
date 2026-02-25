import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from ia.models import PromptImagem


TEST_MEDIA_ROOT = Path(settings.BASE_DIR) / "test_media"


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class StudioViewTests(TestCase):
    """Testes para o fluxo de geracao de imagens."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            email="atelie@test.com",
            password="testpass123",
            is_atelie=True,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client.force_login(self.user)

    def test_studio_view_requires_authentication(self):
        self.client.logout()
        response = self.client.get(reverse("ia:studio"))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(reverse("ia:studio"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("historico", response.context)

    def test_gerar_imagem_valida_prompt_obrigatorio(self):
        response = self.client.post(reverse("ia:gerar_imagem"), {"prompt": "", "size": "512x512"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(PromptImagem.objects.count(), 0)

    def test_gerar_imagem_sucesso_cria_registro(self):
        mock_provider = MagicMock()
        mock_provider.generate_image.return_value = {
            "success": True,
            "url": "https://example.com/fake.png",
            "error": None,
            "metadata": {"model": "dall-e-3"},
        }
        mock_provider.get_provider_name.return_value = "OpenAI DALL-E"

        mock_response = MagicMock()
        mock_response.content = b"fake-bytes"
        mock_response.headers = {"Content-Type": "image/png"}
        mock_response.raise_for_status.return_value = None

        with patch("ia.views.get_image_provider", return_value=mock_provider), \
             patch("ia.views.requests.get", return_value=mock_response):
            response = self.client.post(
                reverse("ia:gerar_imagem"),
                {"prompt": "Vestido dourado", "size": "512x512"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(PromptImagem.objects.count(), 1)
        registro = PromptImagem.objects.first()
        self.assertTrue(registro.sucesso)
        self.assertTrue(registro.arquivo.name)
        self.assertEqual(registro.modelo, "dall-e-3")

    def test_gerar_imagem_falha_registra_erro(self):
        mock_provider = MagicMock()
        mock_provider.generate_image.return_value = {
            "success": False,
            "url": None,
            "error": "Limite atingido",
            "metadata": {},
        }
        mock_provider.get_provider_name.return_value = "OpenAI DALL-E"

        with patch("ia.views.get_image_provider", return_value=mock_provider):
            response = self.client.post(
                reverse("ia:gerar_imagem"),
                {"prompt": "Look vermelho", "size": "512x512"},
            )

        self.assertEqual(response.status_code, 502)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(PromptImagem.objects.count(), 1)
        registro = PromptImagem.objects.first()
        self.assertFalse(registro.sucesso)
        self.assertEqual(registro.mensagem_erro, "Limite atingido")
