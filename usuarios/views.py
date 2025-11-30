"""
Views do app usuarios.
"""
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Count, Max, Q, Prefetch
from .forms import CadastroClienteForm, CadastroAtelieForm, PedidoClienteForm
import requests
from atelie.models import Pedido, ItemPedido, ChatMensagem
from atelie.forms import PedidoClienteEditForm


def cadastro_cliente(request):
    """View para cadastro de cliente."""
    if request.method == 'POST':
        form = CadastroClienteForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('usuarios:redirect_dashboard')
    else:
        form = CadastroClienteForm()
    
    return render(request, 'usuarios/cadastro_cliente.html', {'form': form})


def cadastro_atelie(request):
    """View para cadastro de ateliê."""
    if request.method == 'POST':
        form = CadastroAtelieForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('usuarios:redirect_dashboard')
    else:
        form = CadastroAtelieForm()
    
    return render(request, 'usuarios/cadastro_atelie.html', {'form': form})


def login_view(request):
    """View para login."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bem-vindo(a), {user.email}!')
            return redirect('usuarios:redirect_dashboard')
        else:
            messages.error(request, 'E-mail ou senha incorretos.')
    
    return render(request, 'usuarios/login.html')


@login_required
def logout_view(request):
    """View para logout."""
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('home')


@login_required
def redirect_dashboard(request):
    """Redireciona para o dashboard apropriado baseado no tipo de usuário."""
    user = request.user
    
    if user.is_atelie:
        return redirect('atelie:dashboard')
    elif user.is_cliente:
        return redirect('usuarios:cliente_dashboard')
    else:
        messages.warning(request, 'Tipo de usuário não definido.')
        return redirect('home')


@login_required
def cliente_dashboard(request):
    """Dashboard do cliente."""
    pedidos = (
        Pedido.objects.filter(cliente=request.user)
        .prefetch_related('itens__produto', 'itens__servico')
        .order_by('-data_agendada', '-criado_em')
    )
    
    context = {
        'pedidos': pedidos[:10],
        'total_pedidos': pedidos.count(),
    }
    
    return render(request, 'usuarios/cliente_dashboard.html', context)


@login_required
def meus_chats(request):
    """Lista todas as conversas do cliente."""
    if not request.user.is_cliente:
        messages.warning(request, 'Somente clientes podem acessar seus chats.')
        return redirect('usuarios:redirect_dashboard')
    
    prefetch = Prefetch(
        'mensagens',
        queryset=ChatMensagem.objects.select_related('autor').order_by('-criado_em'),
        to_attr='mensagens_ordenadas'
    )
    pedidos = (
        Pedido.objects.filter(cliente=request.user, mensagens__isnull=False)
        .annotate(
            ultima_mensagem=Max('mensagens__criado_em'),
            nao_lidas=Count('mensagens', filter=Q(mensagens__lida_por_cliente=False))
        )
        .select_related('atelie')
        .prefetch_related(prefetch, 'itens__produto', 'itens__servico')
        .order_by('-ultima_mensagem')
    )
    pedidos = list(pedidos)
    for pedido in pedidos:
        mensagens = getattr(pedido, 'mensagens_ordenadas', [])
        pedido.ultima_mensagem_obj = mensagens[0] if mensagens else None
    
    return render(request, 'usuarios/chats_list.html', {'pedidos': pedidos})


@login_required
def novo_pedido(request):
    """Fluxo para clientes criarem pedidos com agendamento."""
    if not request.user.is_cliente:
        messages.warning(request, 'Somente clientes podem criar pedidos.')
        return redirect('usuarios:redirect_dashboard')
    
    if request.method == 'POST':
        form = PedidoClienteForm(request.POST)
        if form.is_valid():
            pedido = Pedido.objects.create(
                cliente=request.user,
                atelie=form.cleaned_data['atelie'],
                status='AGUARDANDO_ORCAMENTO',
                observacoes=form.cleaned_data['observacoes'],
                data_agendada=form.cleaned_data['data_agendada'],
                hora_agendada=form.cleaned_data['hora_agendada'],
            )
            for produto in form.cleaned_data['produtos']:
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    qtde=1,
                    preco_unitario=produto.preco_base
                )
            for servico in form.cleaned_data['servicos']:
                ItemPedido.objects.create(
                    pedido=pedido,
                    servico=servico,
                    qtde=1,
                    preco_unitario=servico.preco_base
                )
            pedido.calcular_valor_total()
            messages.success(request, 'Pedido criado e agendado com sucesso!')
            return redirect('usuarios:cliente_dashboard')
    else:
        form = PedidoClienteForm()
    
    return render(request, 'usuarios/pedido_form.html', {'form': form})


@login_required
def pedido_edit_cliente(request, pk):
    """Edição de pedido pelo cliente com validações de status e propriedade."""
    if not request.user.is_cliente:
        messages.warning(request, 'Somente clientes podem editar pedidos de cliente.')
        return redirect('usuarios:redirect_dashboard')

    pedido = get_object_or_404(Pedido, pk=pk)
    if pedido.cliente_id != request.user.id:
        raise Http404

    # apenas enquanto status permitir
    if pedido.status not in ['AGUARDANDO_ORCAMENTO', 'AGUARDANDO_APROVACAO', 'AGUARDANDO_PAGAMENTO']:
        messages.error(request, 'Não é possível editar este pedido no status atual.')
        return redirect('usuarios:cliente_dashboard')

    if request.method == 'POST':
        form = PedidoClienteEditForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pedido atualizado com sucesso.')
            return redirect('usuarios:cliente_dashboard')
    else:
        form = PedidoClienteEditForm(instance=pedido)

    return render(request, 'usuarios/pedido_edit_form.html', {'form': form, 'pedido': pedido, 'action': 'Editar Pedido'})


@require_http_methods(["GET"])
def api_cep(request, cep):
    """
    Proxy para API ViaCEP.
    Retorna dados de endereço a partir do CEP.
    """
    try:
        # Limpar CEP (remover caracteres não numéricos)
        cep_limpo = ''.join(filter(str.isdigit, cep))
        
        if len(cep_limpo) != 8:
            return JsonResponse({'error': 'CEP inválido'}, status=400)
        
        # Consultar ViaCEP
        response = requests.get(f'https://viacep.com.br/ws/{cep_limpo}/json/', timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if 'erro' in data:
            return JsonResponse({'error': 'CEP não encontrado'}, status=404)
        
        # Retornar dados padronizados
        return JsonResponse({
            'cep': data.get('cep', ''),
            'logradouro': data.get('logradouro', ''),
            'complemento': data.get('complemento', ''),
            'bairro': data.get('bairro', ''),
            'localidade': data.get('localidade', ''),
            'uf': data.get('uf', ''),
            'ibge': data.get('ibge', ''),
        })
    
    except requests.RequestException as e:
        return JsonResponse({'error': f'Erro ao consultar CEP: {str(e)}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)
