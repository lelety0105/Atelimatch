
from django.urls import path
from .views import chat_page, chat_api, gerar_imagem, studio

app_name = "ia"

urlpatterns = [
    path("studio/", studio, name="studio"),
    path("studio/gerar/", gerar_imagem, name="gerar_imagem"),
    path("chat/", chat_page, name="chat_page"),
    path("api/chat/", chat_api, name="chat_api"),
]
