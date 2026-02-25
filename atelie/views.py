"""
Views do app atelie.
"""

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models
from django.db.models import Count, Max, Prefetch, Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import (
    EstoqueItemForm,
    ItemPedidoForm,
    PedidoAtelieEditForm,
    PedidoClienteEditForm,
    PedidoForm,
    ProdutoForm,
    ServicoForm,
)
from .models import ChatMensagem, EstoqueItem, ItemPedido, Pedido, Produto, Servico


def is_atelie(user):
    """Verifica se o usuario e um atelie."""
    return user.is_authenticated and getattr(user, "is_atelie", False)


@login_required
@user_passes_test(is_atelie)
def dashboard(request):
    """Dashboard do atelie com metricas simples."""
    atelie = request.user.atelie

    pedidos_ativos = (
        Pedido.objects.filter(atelie=atelie)
        .exclude(status__in=["FINALIZADO", "CANCELADO"])
        .count()
    )

    primeiro_dia_mes = timezone.now().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    faturamento_mes = (
        Pedido.objects.filter(
            atelie=atelie, criado_em__gte=primeiro_dia_mes, status="FINALIZADO"
        ).aggregate(total=Sum("valor_total"))["total"]
        or 0
    )

    itens_baixo_estoque = EstoqueItem.objects.filter(
        quantidade_atual__lte=models.F("ponto_reposicao")
    ).count()

    trinta_dias_atras = timezone.now() - timedelta(days=30)
    pedidos_recentes = Pedido.objects.filter(
        atelie=atelie, criado_em__gte=trinta_dias_atras
    )
    pedidos_por_status = (
        pedidos_recentes.values("status").annotate(total=Count("id")).order_by("status")
    )

    context = {
        "pedidos_ativos": pedidos_ativos,
        "faturamento_mes": faturamento_mes,
        "itens_baixo_estoque": itens_baixo_estoque,
        "pedidos_recentes": pedidos_recentes.count(),
        "pedidos_por_status": list(pedidos_por_status),
    }
    return render(request, "atelie/dashboard.html", context)


# CRUD Produtos -------------------------------------------------------------


@login_required
@user_passes_test(is_atelie)
def produto_list(request):
    atelie = request.user.atelie
    produtos = Produto.objects.filter(atelie=atelie).order_by("-criado_em")
    return render(request, "atelie/produto_list.html", {"produtos": produtos})


@login_required
@user_passes_test(is_atelie)
def produto_create(request):
    atelie = request.user.atelie
    if request.method == "POST":
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.atelie = atelie
            produto.save()
            messages.success(request, "Produto criado com sucesso!")
            return redirect("atelie:produto_list")
    else:
        form = ProdutoForm()
    return render(
        request, "atelie/produto_form.html", {"form": form, "action": "Criar"}
    )


@login_required
@user_passes_test(is_atelie)
def produto_update(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == "POST":
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            obj = form.save(commit=False)
            if obj.atelie_id is None:
                obj.atelie = request.user.atelie
            obj.save()
            messages.success(request, "Produto atualizado com sucesso!")
            return redirect("atelie:produto_list")
    else:
        form = ProdutoForm(instance=produto)
    return render(
        request, "atelie/produto_form.html", {"form": form, "action": "Editar"}
    )


@login_required
@user_passes_test(is_atelie)
def produto_delete(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == "POST":
        produto.delete()
        messages.success(request, "Produto deletado com sucesso!")
        return redirect("atelie:produto_list")
    return render(request, "atelie/produto_confirm_delete.html", {"produto": produto})


# CRUD Servicos -------------------------------------------------------------


@login_required
@user_passes_test(is_atelie)
def servico_list(request):
    atelie = request.user.atelie
    servicos = Servico.objects.filter(atelie=atelie).order_by("-criado_em")
    return render(request, "atelie/servico_list.html", {"servicos": servicos})


@login_required
@user_passes_test(is_atelie)
def servico_create(request):
    atelie = request.user.atelie
    if request.method == "POST":
        form = ServicoForm(request.POST)
        if form.is_valid():
            servico = form.save(commit=False)
            servico.atelie = atelie
            servico.save()
            messages.success(request, "Servico criado com sucesso!")
            return redirect("atelie:servico_list")
    else:
        form = ServicoForm()
    return render(
        request, "atelie/servico_form.html", {"form": form, "action": "Criar"}
    )


@login_required
@user_passes_test(is_atelie)
def servico_update(request, pk):
    servico = get_object_or_404(Servico, pk=pk)
    if request.method == "POST":
        form = ServicoForm(request.POST, instance=servico)
        if form.is_valid():
            obj = form.save(commit=False)
            if obj.atelie_id is None:
                obj.atelie = request.user.atelie
            obj.save()
            messages.success(request, "Servico atualizado com sucesso!")
            return redirect("atelie:servico_list")
    else:
        form = ServicoForm(instance=servico)
    return render(
        request, "atelie/servico_form.html", {"form": form, "action": "Editar"}
    )


@login_required
@user_passes_test(is_atelie)
def servico_delete(request, pk):
    servico = get_object_or_404(Servico, pk=pk)
    if request.method == "POST":
        servico.delete()
        messages.success(request, "Servico deletado com sucesso!")
        return redirect("atelie:servico_list")
    return render(request, "atelie/servico_confirm_delete.html", {"servico": servico})


# Estoque -------------------------------------------------------------------


@login_required
@user_passes_test(is_atelie)
def estoque_list(request):
    atelie = request.user.atelie
    itens = (
        EstoqueItem.objects.select_related("produto")
        .filter(produto__atelie=atelie)
        .order_by("produto__nome")
    )
    # template espera a variavel "estoque"
    return render(request, "atelie/estoque_list.html", {"estoque": itens})


@login_required
@user_passes_test(is_atelie)
def estoque_create(request):
    atelie = request.user.atelie
    if request.method == "POST":
        form = EstoqueItemForm(request.POST, atelie=atelie)
        if form.is_valid():
            form.save()
            messages.success(request, "Item de estoque criado com sucesso!")
            return redirect("atelie:estoque_list")
    else:
        form = EstoqueItemForm(atelie=atelie)
    return render(
        request, "atelie/estoque_form.html", {"form": form, "action": "Criar"}
    )


@login_required
@user_passes_test(is_atelie)
def estoque_update(request, pk):
    atelie = request.user.atelie
    estoque = get_object_or_404(EstoqueItem, pk=pk, produto__atelie=atelie)
    if request.method == "POST":
        form = EstoqueItemForm(request.POST, instance=estoque, atelie=atelie)
        if form.is_valid():
            form.save()
            messages.success(request, "Item de estoque atualizado com sucesso!")
            return redirect("atelie:estoque_list")
    else:
        form = EstoqueItemForm(instance=estoque, atelie=atelie)
    return render(
        request, "atelie/estoque_form.html", {"form": form, "action": "Editar"}
    )


# CRUD Pedidos --------------------------------------------------------------


@login_required
@user_passes_test(is_atelie)
def pedido_list(request):
    """Lista de pedidos do atelie logado."""
    atelie = request.user.atelie
    pedidos = Pedido.objects.filter(atelie=atelie)

    status = request.GET.get("status")
    data = request.GET.get("data")
    if status:
        pedidos = pedidos.filter(status=status)
    if data:
        pedidos = pedidos.filter(data_agendada=data)

    pedidos = pedidos.order_by("-data_agendada", "-criado_em").prefetch_related(
        "itens__produto",
        "itens__servico",
    )

    context = {
        "pedidos": pedidos,
        "status_choices": Pedido.STATUS_CHOICES,
        "status_selecionado": status or "",
        "data_filtrada": data or "",
    }
    return render(request, "atelie/pedido_list.html", context)


@login_required
@user_passes_test(is_atelie)
def pedido_detail(request, pk):
    """Detalhe do pedido."""
    pedido = get_object_or_404(Pedido, pk=pk)
    itens = pedido.itens.select_related("produto", "servico")

    user = request.user
    pode_editar_atelie = False
    pode_editar_cliente = False
    if user.is_authenticated and user.is_atelie and hasattr(user, "atelie"):
        pode_editar_atelie = (
            pedido.atelie_id == getattr(user.atelie, "id", None)
            and pedido.status not in ["FINALIZADO", "CANCELADO"]
        )
    if user.is_authenticated and getattr(user, "is_cliente", False):
        pode_editar_cliente = (
            pedido.cliente_id == user.id
            and pedido.status
            in ["AGUARDANDO_ORCAMENTO", "AGUARDANDO_APROVACAO", "AGUARDANDO_PAGAMENTO"]
        )

    return render(
        request,
        "atelie/pedido_detail.html",
        {
            "pedido": pedido,
            "itens": itens,
            "pode_editar_atelie": pode_editar_atelie,
            "pode_editar_cliente": pode_editar_cliente,
        },
    )


@login_required
@user_passes_test(is_atelie)
def pedido_edit_atelie(request, pk):
    """Edicao de pedido pelo atelie (ajuste de orcamento/prazo)."""
    pedido = get_object_or_404(Pedido, pk=pk)
    if not hasattr(request.user, "atelie") or pedido.atelie_id != request.user.atelie.id:
        raise Http404
    if pedido.status in ["FINALIZADO", "CANCELADO"]:
        messages.error(
            request, "Nao e possivel editar pedidos finalizados ou cancelados."
        )
        return redirect("atelie:pedido_detail", pk=pedido.pk)

    if request.method == "POST":
        form = PedidoAtelieEditForm(request.POST, instance=pedido)
        if form.is_valid():
            pedido_obj = form.save(commit=False)
            pedido_obj.status = "AGUARDANDO_APROVACAO"
            pedido_obj.save()
            messages.success(request, "Pedido atualizado com sucesso.")
            return redirect("atelie:pedido_detail", pk=pedido.pk)
    else:
        form = PedidoAtelieEditForm(instance=pedido)

    return render(
        request,
        "atelie/pedido_edit_form.html",
        {"form": form, "pedido": pedido, "action": "Editar (Atelie)"},
    )


@login_required
@user_passes_test(is_atelie)
@require_http_methods(["POST"])
def pedido_cancelar_atelie(request, pk):
    """Cancelamento de pedido pelo atelie (muda status para CANCELADO)."""
    pedido = get_object_or_404(Pedido, pk=pk)
    if not hasattr(request.user, "atelie") or pedido.atelie_id != request.user.atelie.id:
        raise Http404
    if pedido.status in ["FINALIZADO", "EM_ANDAMENTO"]:
        messages.error(
            request, "Nao e possivel cancelar pedidos em andamento ou finalizados."
        )
        return redirect("atelie:pedido_detail", pk=pedido.pk)
    pedido.status = "CANCELADO"
    pedido.save(update_fields=["status"])
    messages.success(request, "Pedido cancelado com sucesso.")
    return redirect("atelie:pedido_detail", pk=pedido.pk)


# Chats ---------------------------------------------------------------------


@login_required
@user_passes_test(is_atelie)
def chats(request):
    """Lista de conversas do atelie por pedido."""
    atelie = request.user.atelie

    prefetch = Prefetch(
        "mensagens",
        queryset=ChatMensagem.objects.select_related("autor").order_by("-criado_em"),
        to_attr="mensagens_ordenadas",
    )
    pedidos = (
        Pedido.objects.filter(atelie=atelie, mensagens__isnull=False)
        .annotate(
            ultima_mensagem=Max("mensagens__criado_em"),
            nao_lidas=Count(
                "mensagens", filter=Q(mensagens__lida_por_atelie=False)
            ),
        )
        .select_related("cliente")
        .prefetch_related(prefetch, "itens__produto", "itens__servico")
        .order_by("-ultima_mensagem")
    )
    pedidos = list(pedidos)
    for pedido in pedidos:
        mensagens = getattr(pedido, "mensagens_ordenadas", [])
        pedido.ultima_mensagem_obj = mensagens[0] if mensagens else None

    return render(request, "atelie/chats_list.html", {"pedidos": pedidos})


@login_required
def pedido_chat(request, pk):
    """Tela de chat do pedido (cliente ou atelie)."""
    pedido = get_object_or_404(Pedido, pk=pk)
    user = request.user
    is_cliente = (
        user.is_authenticated and getattr(user, "is_cliente", False)
        and pedido.cliente_id == user.id
    )
    is_atelie_user = (
        user.is_authenticated
        and getattr(user, "is_atelie", False)
        and hasattr(user, "atelie")
        and pedido.atelie_id == getattr(user.atelie, "id", None)
    )
    if not (is_cliente or is_atelie_user):
        raise Http404

    if request.method == "POST":
        conteudo = (request.POST.get("mensagem") or "").strip()
        if conteudo:
            ChatMensagem.objects.create(
                pedido=pedido,
                autor=user,
                conteudo=conteudo,
                lida_por_cliente=getattr(user, "is_cliente", False),
                lida_por_atelie=getattr(user, "is_atelie", False),
            )
            return redirect("atelie:pedido_chat", pk=pedido.pk)
        messages.error(request, "Mensagem nao pode ser vazia.")

    if is_cliente:
        pedido.mensagens.filter(lida_por_cliente=False).exclude(autor=user).update(
            lida_por_cliente=True
        )
    elif is_atelie_user:
        pedido.mensagens.filter(lida_por_atelie=False).exclude(autor=user).update(
            lida_por_atelie=True
        )

    mensagens = pedido.mensagens.select_related("autor").order_by("criado_em")

    return render(
        request,
        "atelie/pedido_chat.html",
        {"pedido": pedido, "mensagens": mensagens, "eh_cliente": is_cliente},
    )
