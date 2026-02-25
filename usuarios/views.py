"""
Views do app usuarios.
"""

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max, Prefetch, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from atelie.forms import PedidoClienteEditForm
from atelie.models import ChatMensagem, ItemPedido, Pedido
from .forms import CadastroAtelieForm, CadastroClienteForm, PedidoClienteForm
from .models import Atelie


def cadastro_cliente(request):
    """View para cadastro de cliente."""
    if request.method == "POST":
        form = CadastroClienteForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect("usuarios:redirect_dashboard")
    else:
        form = CadastroClienteForm()

    return render(request, "usuarios/cadastro_cliente.html", {"form": form})


def cadastro_atelie(request):
    """View para cadastro de atelie."""
    if request.method == "POST":
        form = CadastroAtelieForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect("usuarios:redirect_dashboard")
    else:
        form = CadastroAtelieForm()

    return render(request, "usuarios/cadastro_atelie.html", {"form": form})


def login_view(request):
    """View para login."""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Bem-vindo(a), {user.email}!")
            return redirect("usuarios:redirect_dashboard")
        else:
            messages.error(request, "E-mail ou senha incorretos.")

    return render(request, "usuarios/login.html")


@login_required
def logout_view(request):
    """View para logout."""
    logout(request)
    messages.info(request, "Voce saiu da sua conta.")
    return redirect("home")


@login_required
def redirect_dashboard(request):
    """Redireciona para o dashboard apropriado baseado no tipo de usuario."""
    user = request.user

    if user.is_atelie:
        return redirect("atelie:dashboard")
    if user.is_cliente:
        return redirect("usuarios:cliente_dashboard")

    messages.warning(request, "Tipo de usuario nao definido.")
    return redirect("home")


@login_required
def cliente_dashboard(request):
    """Dashboard do cliente."""
    pedidos = (
        Pedido.objects.filter(cliente=request.user)
        .prefetch_related("itens__produto", "itens__servico")
        .order_by("-data_agendada", "-criado_em")
    )

    context = {
        "pedidos": pedidos[:10],
        "total_pedidos": pedidos.count(),
    }

    return render(request, "usuarios/cliente_dashboard.html", context)


@login_required
def meus_chats(request):
    """Lista todas as conversas do cliente."""
    if not request.user.is_cliente:
        messages.warning(request, "Somente clientes podem acessar seus chats.")
        return redirect("usuarios:redirect_dashboard")

    prefetch = Prefetch(
        "mensagens",
        queryset=ChatMensagem.objects.select_related("autor").order_by("-criado_em"),
        to_attr="mensagens_ordenadas",
    )
    pedidos = (
        Pedido.objects.filter(cliente=request.user, mensagens__isnull=False)
        .annotate(
            ultima_mensagem=Max("mensagens__criado_em"),
            nao_lidas=Count(
                "mensagens", filter=Q(mensagens__lida_por_cliente=False)
            ),
        )
        .select_related("atelie")
        .prefetch_related(prefetch, "itens__produto", "itens__servico")
        .order_by("-ultima_mensagem")
    )
    pedidos = list(pedidos)
    for pedido in pedidos:
        mensagens = getattr(pedido, "mensagens_ordenadas", [])
        pedido.ultima_mensagem_obj = mensagens[0] if mensagens else None

    return render(request, "usuarios/chats_list.html", {"pedidos": pedidos})


@login_required
def novo_pedido(request):
    """Fluxo para clientes criarem pedidos com agendamento."""
    if not request.user.is_cliente:
        messages.warning(request, "Somente clientes podem criar pedidos.")
        return redirect("usuarios:redirect_dashboard")

    if request.method == "POST":
        form = PedidoClienteForm(request.POST)
        if form.is_valid():
            pedido = Pedido.objects.create(
                cliente=request.user,
                atelie=form.cleaned_data["atelie"],
                status="AGUARDANDO_ORCAMENTO",
                observacoes=form.cleaned_data["observacoes"],
                data_agendada=form.cleaned_data["data_agendada"],
                hora_agendada=form.cleaned_data["hora_agendada"],
            )
            produto = form.cleaned_data.get("produto")
            servico = form.cleaned_data.get("servico")
            if produto:
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    qtde=1,
                    preco_unitario=produto.preco_base,
                )
            if servico:
                ItemPedido.objects.create(
                    pedido=pedido,
                    servico=servico,
                    qtde=1,
                    preco_unitario=servico.preco_base,
                )
            pedido.calcular_valor_total()
            messages.success(request, "Pedido criado e agendado com sucesso!")
            return redirect("usuarios:cliente_dashboard")
    else:
        # Permitir que o atelie seja pre-selecionado via querystring (ex: mapa)
        atelie_id = request.GET.get("atelie_id")
        initial = {}
        atelie_obj = None
        if atelie_id:
            try:
                atelie_obj = Atelie.objects.get(pk=atelie_id, ativo=True)
                initial["atelie"] = atelie_obj
            except Atelie.DoesNotExist:
                atelie_obj = None
        form = PedidoClienteForm(initial=initial, atelie=atelie_obj)

    return render(request, "usuarios/pedido_form.html", {"form": form})


@login_required
def pedido_edit_cliente(request, pk):
    """Edicao de pedido pelo cliente com validacoes de status e propriedade."""
    if not request.user.is_cliente:
        messages.warning(request, "Somente clientes podem editar pedidos de cliente.")
        return redirect("usuarios:redirect_dashboard")

    pedido = get_object_or_404(Pedido, pk=pk)
    if pedido.cliente_id != request.user.id:
        raise Http404

    # apenas enquanto status permitir
    if pedido.status not in [
        "AGUARDANDO_ORCAMENTO",
        "AGUARDANDO_APROVACAO",
        "AGUARDANDO_PAGAMENTO",
    ]:
        messages.error(
            request,
            "Nao e possivel editar este pedido no status atual.",
        )
        return redirect("usuarios:cliente_dashboard")

    if request.method == "POST":
        form = PedidoClienteEditForm(request.POST, instance=pedido)
        if form.is_valid():
            pedido_obj = form.save(commit=False)
            # sempre que o cliente editar, volta para aguardando orcamento
            pedido_obj.status = "AGUARDANDO_ORCAMENTO"
            pedido_obj.save()
            # atualizar itens (produtos/servicos) e valor total
            form.save_items(pedido_obj)
            pedido_obj.calcular_valor_total()
            messages.success(request, "Pedido atualizado com sucesso.")
            return redirect("usuarios:cliente_dashboard")
    else:
        form = PedidoClienteEditForm(instance=pedido)

    return render(
        request,
        "usuarios/pedido_edit_form.html",
        {"form": form, "pedido": pedido, "action": "Editar Pedido"},
    )


@login_required
@require_http_methods(["POST"])
def pedido_cancelar_cliente(request, pk):
    """Cancelamento de pedido pelo cliente (muda status para CANCELADO)."""
    if not request.user.is_cliente:
        messages.warning(request, "Somente clientes podem cancelar pedidos.")
        return redirect("usuarios:redirect_dashboard")

    pedido = get_object_or_404(Pedido, pk=pk, cliente=request.user)
    if pedido.status in ["FINALIZADO", "EM_ANDAMENTO"]:
        messages.error(
            request, "Nao e possivel cancelar pedidos em andamento ou finalizados."
        )
        return redirect("usuarios:cliente_dashboard")

    pedido.status = "CANCELADO"
    pedido.save(update_fields=["status"])
    messages.success(request, "Pedido cancelado com sucesso.")
    return redirect("usuarios:cliente_dashboard")


@require_http_methods(["GET"])
def api_cep(request, cep):
    """
    Proxy para API ViaCEP.
    Retorna dados de endereco a partir do CEP.
    """
    try:
        cep_limpo = "".join(filter(str.isdigit, cep))

        if len(cep_limpo) != 8:
            return JsonResponse({"error": "CEP invalido"}, status=400)

        response = requests.get(
            f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5
        )
        response.raise_for_status()

        data = response.json()

        if "erro" in data:
            return JsonResponse({"error": "CEP nao encontrado"}, status=404)

        return JsonResponse(
            {
                "cep": data.get("cep", ""),
                "logradouro": data.get("logradouro", ""),
                "complemento": data.get("complemento", ""),
                "bairro": data.get("bairro", ""),
                "localidade": data.get("localidade", ""),
                "uf": data.get("uf", ""),
                "ibge": data.get("ibge", ""),
            }
        )

    except requests.RequestException as exc:
        return JsonResponse(
            {"error": f"Erro ao consultar CEP: {str(exc)}"}, status=500
        )
    except Exception as exc:  # pragma: no cover - caminho de erro generico
        return JsonResponse({"error": f"Erro interno: {str(exc)}"}, status=500)


@login_required
def encontrar_atelies(request):
    """Tela para o cliente encontrar atelies no mapa."""
    return render(request, "usuarios/encontrar_atelies.html")


@require_http_methods(["GET"])
def api_atelies_mapa(request):
    """
    Retorna em JSON os atelies ativos com coordenadas para exibicao no mapa.
    Formato usado em templates/usuarios/encontrar_atelies.html.
    """
    atelies = (
        Atelie.objects.filter(ativo=True)
        .exclude(geolocalizacao_lat__isnull=True)
        .exclude(geolocalizacao_lng__isnull=True)
        .select_related("user")
    )

    dados = []
    for atelie in atelies:
        lat = float(atelie.geolocalizacao_lat)
        lng = float(atelie.geolocalizacao_lng)
        dados.append(
            {
                "id": atelie.id,
                "nome": atelie.nome_fantasia,
                "email": atelie.user.email,
                "telefone": atelie.telefone_comercial,
                "endereco": atelie.endereco_completo(),
                "cidade": atelie.cidade,
                "uf": atelie.uf,
                "cep": atelie.cep,
                "especialidades": atelie.especialidades,
                "latitude": lat,
                "longitude": lng,
            }
        )

    return JsonResponse({"success": True, "count": len(dados), "atelies": dados})


@require_http_methods(["GET"])
def api_geocodificar_cep(request, cep):
    """
    Endpoint para geocodificar um CEP e retornar coordenadas (usado no cadastro/edicao de atelie).
    Usa ViaCEP + Nominatim (OSM).
    """
    try:
        cep_limpo = "".join(filter(str.isdigit, cep))
        if len(cep_limpo) != 8:
            return JsonResponse({"error": "CEP invalido"}, status=400)

        response = requests.get(
            f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5
        )
        response.raise_for_status()
        data = response.json()

        if "erro" in data:
            return JsonResponse({"error": "CEP nao encontrado"}, status=404)

        logradouro = data.get("logradouro", "")
        localidade = data.get("localidade", "")
        uf = data.get("uf", "")
        endereco_completo = f"{logradouro}, {localidade}, {uf}, Brasil"

        try:
            geo_response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": endereco_completo, "format": "json", "limit": 1},
                headers={"User-Agent": "Atelimatch"},
                timeout=5,
            )
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            lat = float(geo_data[0]["lat"]) if geo_data else None
            lng = float(geo_data[0]["lon"]) if geo_data else None
        except requests.RequestException:
            lat = None
            lng = None

        return JsonResponse(
            {
                "success": True,
                "cep": data.get("cep", ""),
                "logradouro": data.get("logradouro", ""),
                "complemento": data.get("complemento", ""),
                "bairro": data.get("bairro", ""),
                "localidade": data.get("localidade", ""),
                "uf": data.get("uf", ""),
                "latitude": lat,
                "longitude": lng,
            }
        )
    except requests.RequestException as exc:
        return JsonResponse(
            {"error": f"Erro ao consultar CEP: {str(exc)}"}, status=500
        )
    except Exception as exc:
        return JsonResponse({"error": f"Erro interno: {str(exc)}"}, status=500)
