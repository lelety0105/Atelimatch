"""
Views do app atelie.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q, Max, Prefetch
from django.utils import timezone
from datetime import timedelta
from django.http import Http404
from .models import Produto, EstoqueItem, Pedido, ItemPedido, Servico, ChatMensagem
from .forms import (
    ProdutoForm, EstoqueItemForm, PedidoForm, ItemPedidoForm,
    ServicoForm, PedidoClienteEditForm, PedidoAtelieEditForm
)
from django.db import models


def is_atelie(user):
    """Verifica se o usuário é um ateliê."""
    return user.is_authenticated and user.is_atelie


@login_required
@user_passes_test(is_atelie)
def dashboard(request):
    """Dashboard do ateliê com métricas."""
    atelie = request.user.atelie
    
    # Pedidos ativos (não finalizados ou cancelados)
    pedidos_ativos = Pedido.objects.filter(
        atelie=atelie
    ).exclude(status__in=['FINALIZADO', 'CANCELADO']).count()
    
    # Faturamento do mês
    primeiro_dia_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    faturamento_mes = Pedido.objects.filter(
        atelie=atelie,
        criado_em__gte=primeiro_dia_mes,
        status='FINALIZADO'
    ).aggregate(total=Sum('valor_total'))['total'] or 0
    
    # Itens em baixo estoque
    itens_baixo_estoque = EstoqueItem.objects.filter(
        quantidade_atual__lte=models.F('ponto_reposicao')
    ).count()
    
    # Pedidos no prazo (últimos 30 dias)
    trinta_dias_atras = timezone.now() - timedelta(days=30)
    pedidos_recentes = Pedido.objects.filter(
        atelie=atelie,
        criado_em__gte=trinta_dias_atras
    )
    
    # Dados para gráfico (pedidos por status)
    pedidos_por_status = pedidos_recentes.values('status').annotate(
        total=Count('id')
    ).order_by('status')
    
    context = {
        'pedidos_ativos': pedidos_ativos,
        'faturamento_mes': faturamento_mes,
        'itens_baixo_estoque': itens_baixo_estoque,
        'pedidos_recentes': pedidos_recentes.count(),
        'pedidos_por_status': list(pedidos_por_status),
    }
    
    return render(request, 'atelie/dashboard.html', context)


# CRUD Produtos
@login_required
@user_passes_test(is_atelie)
def produto_list(request):
    """Lista de produtos."""
    produtos = Produto.objects.all().order_by('-criado_em')
    return render(request, 'atelie/produto_list.html', {'produtos': produtos})


@login_required
@user_passes_test(is_atelie)
def produto_create(request):
    """Criar produto."""
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto criado com sucesso!')
            return redirect('atelie:produto_list')
    else:
        form = ProdutoForm()
    
    return render(request, 'atelie/produto_form.html', {'form': form, 'action': 'Criar'})


@login_required
@user_passes_test(is_atelie)
def produto_update(request, pk):
    """Atualizar produto."""
    produto = get_object_or_404(Produto, pk=pk)
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('atelie:produto_list')
    else:
        form = ProdutoForm(instance=produto)
    
    return render(request, 'atelie/produto_form.html', {'form': form, 'action': 'Editar'})


@login_required
@user_passes_test(is_atelie)
def produto_delete(request, pk):
    """Deletar produto."""
    produto = get_object_or_404(Produto, pk=pk)
    
    if request.method == 'POST':
        produto.delete()
        messages.success(request, 'Produto deletado com sucesso!')
        return redirect('atelie:produto_list')
    
    return render(request, 'atelie/produto_confirm_delete.html', {'produto': produto})


# CRUD Serviços
@login_required
@user_passes_test(is_atelie)
def servico_list(request):
    servicos = Servico.objects.all().order_by('-criado_em')
    return render(request, 'atelie/servico_list.html', {'servicos': servicos})


@login_required
@user_passes_test(is_atelie)
def servico_create(request):
    if request.method == 'POST':
        form = ServicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Serviço criado com sucesso!')
            return redirect('atelie:servico_list')
    else:
        form = ServicoForm()
    return render(request, 'atelie/servico_form.html', {'form': form, 'action': 'Criar'})


@login_required
@user_passes_test(is_atelie)
def servico_update(request, pk):
    servico = get_object_or_404(Servico, pk=pk)
    if request.method == 'POST':
        form = ServicoForm(request.POST, instance=servico)
        if form.is_valid():
            form.save()
            messages.success(request, 'Serviço atualizado com sucesso!')
            return redirect('atelie:servico_list')
    else:
        form = ServicoForm(instance=servico)
    return render(request, 'atelie/servico_form.html', {'form': form, 'action': 'Editar'})


@login_required
@user_passes_test(is_atelie)
def servico_delete(request, pk):
    servico = get_object_or_404(Servico, pk=pk)
    if request.method == 'POST':
        servico.delete()
        messages.success(request, 'Serviço removido com sucesso!')
        return redirect('atelie:servico_list')
    return render(request, 'atelie/servico_confirm_delete.html', {'servico': servico})


@login_required
@user_passes_test(is_atelie)
def chats(request):
    """Lista de conversas do ateliê."""
    atelie = request.user.atelie
    status = request.GET.get('status', '')
    unread = request.GET.get('unread', '')
    prefetch = Prefetch(
        'mensagens',
        queryset=ChatMensagem.objects.select_related('autor').order_by('-criado_em'),
        to_attr='mensagens_ordenadas'
    )
    pedidos = (
        Pedido.objects.filter(atelie=atelie, mensagens__isnull=False)
        .annotate(
            ultima_mensagem=Max('mensagens__criado_em'),
            nao_lidas=Count('mensagens', filter=Q(mensagens__lida_por_atelie=False))
        )
        .select_related('cliente')
        .prefetch_related(prefetch, 'itens__produto', 'itens__servico')
    )
    if status:
        pedidos = pedidos.filter(status=status)
    if unread == '1':
        pedidos = pedidos.filter(nao_lidas__gt=0)
    pedidos = pedidos.order_by('-ultima_mensagem')
    pedidos = list(pedidos)
    for pedido in pedidos:
        mensagens = getattr(pedido, 'mensagens_ordenadas', [])
        pedido.ultima_mensagem_obj = mensagens[0] if mensagens else None
    
    context = {
        'pedidos': pedidos,
        'status_choices': Pedido.STATUS_CHOICES,
        'status_selecionado': status,
        'somente_nao_lidas': unread == '1',
    }
    return render(request, 'atelie/chats_list.html', context)


# CRUD Estoque
@login_required
@user_passes_test(is_atelie)
def estoque_list(request):
    """Lista de estoque."""
    estoque = EstoqueItem.objects.select_related('produto').all()
    return render(request, 'atelie/estoque_list.html', {'estoque': estoque})


@login_required
@user_passes_test(is_atelie)
def estoque_create(request):
    """Criar item de estoque."""
    if request.method == 'POST':
        form = EstoqueItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item de estoque criado com sucesso!')
            return redirect('atelie:estoque_list')
    else:
        form = EstoqueItemForm()
    
    return render(request, 'atelie/estoque_form.html', {'form': form, 'action': 'Criar'})


@login_required
@user_passes_test(is_atelie)
def estoque_update(request, pk):
    """Atualizar item de estoque."""
    estoque = get_object_or_404(EstoqueItem, pk=pk)
    
    if request.method == 'POST':
        form = EstoqueItemForm(request.POST, instance=estoque)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item de estoque atualizado com sucesso!')
            return redirect('atelie:estoque_list')
    else:
        form = EstoqueItemForm(instance=estoque)
    
    return render(request, 'atelie/estoque_form.html', {'form': form, 'action': 'Editar'})


# CRUD Pedidos
@login_required
@user_passes_test(is_atelie)
def pedido_list(request):
    """Lista de pedidos."""
    atelie = request.user.atelie
    pedidos = Pedido.objects.filter(atelie=atelie)

    status = request.GET.get('status')
    data = request.GET.get('data')
    if status:
        pedidos = pedidos.filter(status=status)
    if data:
        pedidos = pedidos.filter(data_agendada=data)

    pedidos = pedidos.order_by('-data_agendada', '-criado_em').prefetch_related(
        'itens__produto',
        'itens__servico'
    )

    context = {
        'pedidos': pedidos,
        'status_choices': Pedido.STATUS_CHOICES,
        'status_selecionado': status or '',
        'data_filtrada': data or '',
    }
    return render(request, 'atelie/pedido_list.html', context)


@login_required
@user_passes_test(is_atelie)
def pedido_detail(request, pk):
    """Detalhe do pedido."""
    pedido = get_object_or_404(Pedido, pk=pk)
    itens = pedido.itens.select_related('produto', 'servico')
    # indicar permissões de edição
    user = request.user
    pode_editar_atelie = False
    pode_editar_cliente = False
    if user.is_authenticated and user.is_atelie and hasattr(user, 'atelie'):
        pode_editar_atelie = (pedido.atelie_id == getattr(user.atelie, 'id', None)) and (pedido.status not in ['FINALIZADO', 'CANCELADO'])
    if user.is_authenticated and user.is_cliente:
        pode_editar_cliente = (pedido.cliente_id == user.id) and (pedido.status in ['AGUARDANDO_ORCAMENTO', 'AGUARDANDO_APROVACAO', 'AGUARDANDO_PAGAMENTO'])

    return render(request, 'atelie/pedido_detail.html', {
        'pedido': pedido,
        'itens': itens,
        'pode_editar_atelie': pode_editar_atelie,
        'pode_editar_cliente': pode_editar_cliente,
    })


@login_required
@user_passes_test(is_atelie)
def pedido_edit_atelie(request, pk):
    """Edição de pedido pelo ateliê."""
    pedido = get_object_or_404(Pedido, pk=pk)
    # validar vínculo
    if not hasattr(request.user, 'atelie') or pedido.atelie_id != request.user.atelie.id:
        raise Http404
    if pedido.status in ['FINALIZADO', 'CANCELADO']:
        messages.error(request, 'Não é possível editar pedidos finalizados ou cancelados.')
        return redirect('atelie:pedido_detail', pk=pedido.pk)

    if request.method == 'POST':
        form = PedidoAtelieEditForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pedido atualizado com sucesso.')
            return redirect('atelie:pedido_detail', pk=pedido.pk)
    else:
        form = PedidoAtelieEditForm(instance=pedido)

    return render(request, 'atelie/pedido_edit_form.html', {'form': form, 'pedido': pedido, 'action': 'Editar (Ateliê)'})


@login_required
def pedido_chat(request, pk):
    """Tela de chat do pedido (cliente ou ateliê)."""
    pedido = get_object_or_404(Pedido, pk=pk)
    user = request.user
    is_cliente = user.is_authenticated and user.is_cliente and pedido.cliente_id == user.id
    is_atelie_user = (
        user.is_authenticated
        and user.is_atelie
        and hasattr(user, 'atelie')
        and pedido.atelie_id == getattr(user.atelie, 'id', None)
    )
    if not (is_cliente or is_atelie_user):
        raise Http404
    
    if request.method == 'POST':
        conteudo = (request.POST.get('mensagem') or '').strip()
        if conteudo:
            ChatMensagem.objects.create(
                pedido=pedido,
                autor=user,
                conteudo=conteudo,
                lida_por_cliente=user.is_cliente,
                lida_por_atelie=user.is_atelie,
            )
            return redirect('atelie:pedido_chat', pk=pedido.pk)
        messages.error(request, 'Mensagem não pode ser vazia.')
    
    if is_cliente:
        pedido.mensagens.filter(lida_por_cliente=False).exclude(autor=user).update(lida_por_cliente=True)
    elif is_atelie_user:
        pedido.mensagens.filter(lida_por_atelie=False).exclude(autor=user).update(lida_por_atelie=True)
    
    mensagens = pedido.mensagens.select_related('autor').order_by('criado_em')
    
    return render(request, 'atelie/pedido_chat.html', {
        'pedido': pedido,
        'mensagens': mensagens,
        'eh_cliente': is_cliente,
    })
