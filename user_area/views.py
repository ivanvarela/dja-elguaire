"""
User Area Views - Authenticated user interface

Matches PHP's /inside/ directory
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from core.models import Polla, Evento, BetPolla, BetEvento, AccountTransaction, EventTransaction
from user_area.forms import BetPollaForm, BetEventoForm


@login_required
def dashboard(request):
    """User dashboard - shows active and past events"""
    # Get active events
    active_pollas = Polla.objects.filter(status='Running', date_race__gt=timezone.now())
    active_eventos = Evento.objects.filter(status='Running')

    # Get past events
    past_pollas = Polla.objects.filter(status__in=['Close', 'Paid']).order_by('-date_race')[:5]
    past_eventos = Evento.objects.filter(status__in=['Close', 'Paid']).order_by('-date')[:5]

    # Get user's balance
    balance = request.user.get_balance()

    context = {
        'title': 'Dashboard',
        'active_pollas': active_pollas,
        'active_eventos': active_eventos,
        'past_pollas': past_pollas,
        'past_eventos': past_eventos,
        'balance': balance,
    }

    return render(request, 'user_area/dashboard.html', context)


@login_required
def place_bet_polla(request, polla_id):
    """Place a bet on a polla"""
    polla = get_object_or_404(Polla, id=polla_id)

    # Check if polla is still open
    if not polla.is_open():
        messages.error(request, 'Esta polla ya está cerrada')
        return redirect('user_area:dashboard')

    # Check if user already placed a bet
    if BetPolla.objects.filter(user=request.user, polla=polla).exists():
        messages.warning(request, 'Ya has realizado una apuesta para esta polla')
        return redirect('user_area:dashboard')

    # Check if user has enough balance
    balance = request.user.get_balance()
    if balance < polla.price_entry:
        messages.error(request, f'Saldo insuficiente. Necesitas ${polla.price_entry}')
        return redirect('user_area:dashboard')

    if request.method == 'POST':
        form = BetPollaForm(request.POST)
        if form.is_valid():
            bet = form.save(commit=False)
            bet.user = request.user
            bet.polla = polla
            bet.credit_cost = -polla.price_entry
            bet.save()

            # Create account transactions
            now = timezone.now()

            # Debit user's account
            AccountTransaction.objects.create(
                user=request.user,
                polla=polla,
                bet=bet,
                tipo='Apuesta',
                comment=f'Apuesta: {polla.code4}',
                qty=-polla.price_entry,
                trx_date=now
            )

            # Calculate commission and pot
            commission = polla.price_entry * 0.10
            acumulado = polla.price_entry * 0.10
            pot = polla.price_entry - commission - acumulado

            # System transactions
            AccountTransaction.objects.create(
                user_id=1,  # System user
                polla=polla,
                bet=bet,
                tipo='Comision',
                comment=f'Comisión sistema - {polla.code4}',
                qty=commission,
                trx_date=now
            )

            AccountTransaction.objects.create(
                user_id=1,
                polla=polla,
                bet=bet,
                tipo='Pote',
                comment=f'Pote a repartir - {polla.code4}',
                qty=pot,
                trx_date=now
            )

            AccountTransaction.objects.create(
                user_id=1,
                polla=polla,
                bet=bet,
                tipo='Acumulado2305',
                comment=f'Acumulado - {polla.code4}',
                qty=acumulado,
                trx_date=now
            )

            messages.success(request, f'Apuesta registrada exitosamente. Se debitó ${polla.price_entry} de tu cuenta.')
            return redirect('user_area:dashboard')
    else:
        form = BetPollaForm()

    context = {
        'title': f'Apostar - {polla.code4}',
        'polla': polla,
        'form': form,
        'balance': request.user.get_balance()
    }

    return render(request, 'user_area/place_bet_polla.html', context)


@login_required
def place_bet_evento(request, evento_id):
    """Place a bet on an evento"""
    evento = get_object_or_404(Evento, id=evento_id)

    # Check if evento is still open
    if not evento.is_open():
        messages.error(request, 'Este evento ya está cerrado')
        return redirect('user_area:dashboard')

    # Check if user already placed a bet
    if BetEvento.objects.filter(user=request.user, evento=evento).exists():
        messages.warning(request, 'Ya has realizado una apuesta para este evento')
        return redirect('user_area:dashboard')

    # Check if user has enough balance
    balance = request.user.get_balance()
    if balance < evento.price_entry:
        messages.error(request, f'Saldo insuficiente. Necesitas ${evento.price_entry}')
        return redirect('user_area:dashboard')

    matches = evento.matches.all().order_by('orden_pa')

    if request.method == 'POST':
        form = BetEventoForm(request.POST, evento=evento, matches=matches)
        if form.is_valid():
            bet = form.save(commit=False)
            bet.user = request.user
            bet.evento = evento
            bet.credit_cost = -evento.price_entry
            bet.save()

            # Save match predictions
            form.save_match_predictions(bet)

            # Create account transactions
            now = timezone.now()

            # Debit user's account
            EventTransaction.objects.create(
                user=request.user,
                evento=evento,
                bet=bet,
                tipo='Apuesta',
                comment=f'Apuesta: {evento.name}',
                qty=-evento.price_entry,
                trx_date=now
            )

            # Calculate commission and pot
            commission = evento.price_entry * 0.15
            pot = evento.price_entry - commission

            # System transactions
            EventTransaction.objects.create(
                user_id=1,  # System user
                evento=evento,
                bet=bet,
                tipo='Comision',
                comment=f'Comisión sistema - {evento.name}',
                qty=commission,
                trx_date=now
            )

            EventTransaction.objects.create(
                user_id=1,
                evento=evento,
                bet=bet,
                tipo='Pote',
                comment=f'Pote a repartir - {evento.name}',
                qty=pot,
                trx_date=now
            )

            messages.success(request, f'Apuesta registrada exitosamente. Se debitó ${evento.price_entry} de tu cuenta.')
            return redirect('user_area:dashboard')
    else:
        form = BetEventoForm(evento=evento, matches=matches)

    context = {
        'title': f'Apostar - {evento.name}',
        'evento': evento,
        'matches': matches,
        'form': form,
        'balance': request.user.get_balance()
    }

    return render(request, 'user_area/place_bet_evento.html', context)


@login_required
def account_detail(request):
    """Show user's transaction history"""
    account_transactions = AccountTransaction.objects.filter(
        user=request.user
    ).order_by('-trx_date')

    event_transactions = EventTransaction.objects.filter(
        user=request.user
    ).order_by('-trx_date')

    # Merge and sort all transactions
    all_transactions = list(account_transactions) + list(event_transactions)
    all_transactions.sort(key=lambda x: x.trx_date, reverse=True)

    context = {
        'title': 'Detalle de Cuenta',
        'transactions': all_transactions,
        'balance': request.user.get_balance()
    }

    return render(request, 'user_area/account_detail.html', context)


@login_required
def my_bets(request):
    """Show user's betting history"""
    polla_bets = BetPolla.objects.filter(user=request.user).order_by('-date_bet')
    evento_bets = BetEvento.objects.filter(user=request.user).order_by('-date_bet')

    context = {
        'title': 'Mis Apuestas',
        'polla_bets': polla_bets,
        'evento_bets': evento_bets,
    }

    return render(request, 'user_area/my_bets.html', context)


@login_required
def view_results(request, polla_id=None, evento_id=None):
    """View results for a completed event"""
    if polla_id:
        polla = get_object_or_404(Polla, id=polla_id)
        if polla.status == 'Running':
            messages.warning(request, 'Esta polla aún no ha cerrado')
            return redirect('user_area:dashboard')

        # Get winners
        from admin_panel.utils import get_polla_winners
        winners = get_polla_winners(polla)

        context = {
            'title': f'Resultados - {polla.code4}',
            'polla': polla,
            'winners': winners
        }
        return render(request, 'user_area/view_results_polla.html', context)

    elif evento_id:
        evento = get_object_or_404(Evento, id=evento_id)
        if evento.status == 'Running':
            messages.warning(request, 'Este evento aún no ha cerrado')
            return redirect('user_area:dashboard')

        # Get winners
        from admin_panel.utils import get_evento_winners
        winners = get_evento_winners(evento)

        context = {
            'title': f'Resultados - {evento.name}',
            'evento': evento,
            'winners': winners
        }
        return render(request, 'user_area/view_results_evento.html', context)

    else:
        return redirect('user_area:dashboard')
