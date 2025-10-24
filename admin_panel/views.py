"""
Custom Admin Panel Views

This is your custom admin interface (NOT Django's built-in admin).
Matches the PHP /adm/ directory structure with frontend-accessible admin pages.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from core.models import (
    Polla, Evento, Match, Racetrack, League, Team,
    BetPolla, BetEvento, User
)
from admin_panel.decorators import admin_required, superadmin_required
from admin_panel.forms import (
    PollaForm, EventoForm, MatchForm, ResultPollaForm, ResultEventoForm
)


@admin_required
def dashboard(request):
    """Admin dashboard - overview"""
    context = {
        'title': 'Panel Administrativo',
        'total_users': User.objects.count(),
        'active_pollas': Polla.objects.filter(status='Running').count(),
        'active_eventos': Evento.objects.filter(status='Running').count(),
        'recent_pollas': Polla.objects.all().order_by('-created_at')[:5],
        'recent_eventos': Evento.objects.all().order_by('-created_at')[:5],
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ==================== POLLA MANAGEMENT ====================

@admin_required
def manage_pollas(request):
    """List and manage pollas (horse race pools)"""
    pollas = Polla.objects.filter(status__in=['Running', 'Close']).order_by('-date_race')
    return render(request, 'admin_panel/manage_pollas.html', {
        'title': 'Administrar Pollas',
        'pollas': pollas
    })


@admin_required
def create_polla(request):
    """Create new polla"""
    if request.method == 'POST':
        form = PollaForm(request.POST)
        if form.is_valid():
            polla = form.save()
            messages.success(request, f'Polla {polla.code4} creada exitosamente')
            return redirect('admin_panel:manage_pollas')
    else:
        form = PollaForm()

    return render(request, 'admin_panel/create_polla.html', {
        'title': 'Crear Polla',
        'form': form
    })


@admin_required
def delete_polla(request, polla_id):
    """Delete polla (only if no bets placed)"""
    polla = get_object_or_404(Polla, id=polla_id)

    if polla.bets.exists():
        messages.error(request, 'No se puede eliminar una polla con apuestas')
        return redirect('admin_panel:manage_pollas')

    polla.delete()
    messages.success(request, f'Polla {polla.code4} eliminada')
    return redirect('admin_panel:manage_pollas')


# ==================== EVENTO MANAGEMENT ====================

@admin_required
def manage_eventos(request):
    """List and manage eventos (sports events)"""
    eventos = Evento.objects.filter(status__in=['Running', 'Close']).order_by('-date')
    return render(request, 'admin_panel/manage_eventos.html', {
        'title': 'Administrar Eventos',
        'eventos': eventos
    })


@admin_required
def create_evento(request):
    """Create new evento"""
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save()
            messages.success(request, f'Evento {evento.code4} creado exitosamente')
            return redirect('admin_panel:add_matches', evento_id=evento.id)
    else:
        form = EventoForm()

    return render(request, 'admin_panel/create_evento.html', {
        'title': 'Crear Evento',
        'form': form
    })


@admin_required
def add_matches(request, evento_id):
    """Add matches to an evento"""
    evento = get_object_or_404(Evento, id=evento_id)

    if request.method == 'POST':
        form = MatchForm(request.POST, evento=evento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Partido agregado exitosamente')
            return redirect('admin_panel:add_matches', evento_id=evento.id)
    else:
        form = MatchForm(evento=evento)

    matches = evento.matches.all().order_by('orden_pa')

    return render(request, 'admin_panel/add_matches.html', {
        'title': f'Agregar Partidos - {evento.name}',
        'evento': evento,
        'form': form,
        'matches': matches
    })


@admin_required
def delete_evento(request, evento_id):
    """Delete evento (only if no bets placed)"""
    evento = get_object_or_404(Evento, id=evento_id)

    if evento.bets.exists():
        messages.error(request, 'No se puede eliminar un evento con apuestas')
        return redirect('admin_panel:manage_eventos')

    evento.delete()
    messages.success(request, f'Evento {evento.code4} eliminado')
    return redirect('admin_panel:manage_eventos')


# ==================== RESULTS ENTRY ====================

@admin_required
def enter_results_polla(request, polla_id):
    """Enter results for a polla"""
    polla = get_object_or_404(Polla, id=polla_id)

    if polla.status == 'Paid':
        messages.warning(request, 'Esta polla ya fue pagada')
        return redirect('admin_panel:manage_pollas')

    if request.method == 'POST':
        form = ResultPollaForm(request.POST, instance=polla)
        if form.is_valid():
            polla = form.save(commit=False)
            polla.status = 'Close'
            polla.save()

            # Calculate points for all bets
            for bet in polla.bets.all():
                bet.calculate_points()

            messages.success(request, 'Resultados ingresados. Proceder a pagar premios.')
            return redirect('admin_panel:pay_polla', polla_id=polla.id)
    else:
        form = ResultPollaForm(instance=polla)

    return render(request, 'admin_panel/enter_results_polla.html', {
        'title': f'Ingresar Resultados - {polla.code4}',
        'polla': polla,
        'form': form
    })


@admin_required
def enter_results_evento(request, evento_id):
    """Enter results for an evento"""
    evento = get_object_or_404(Evento, id=evento_id)

    if evento.status == 'Paid':
        messages.warning(request, 'Este evento ya fue pagado')
        return redirect('admin_panel:manage_eventos')

    matches = evento.matches.all().order_by('orden_pa')

    if request.method == 'POST':
        # Process match results
        all_results_entered = True
        for match in matches:
            score1 = request.POST.get(f'match_{match.id}_score1')
            score2 = request.POST.get(f'match_{match.id}_score2')

            if score1 and score2:
                match.score_team1 = int(score1)
                match.score_team2 = int(score2)
                match.save()
            else:
                all_results_entered = False

        if all_results_entered:
            evento.status = 'Close'
            evento.save()

            # Calculate points for all bets
            from admin_panel.utils import calculate_evento_points
            calculate_evento_points(evento)

            messages.success(request, 'Resultados ingresados. Proceder a pagar premios.')
            return redirect('admin_panel:pay_evento', evento_id=evento.id)
        else:
            messages.error(request, 'Debes ingresar resultados para todos los partidos')

    return render(request, 'admin_panel/enter_results_evento.html', {
        'title': f'Ingresar Resultados - {evento.name}',
        'evento': evento,
        'matches': matches
    })


# ==================== PRIZE PAYMENT ====================

@admin_required
def pay_polla(request, polla_id):
    """Process prize payments for polla"""
    polla = get_object_or_404(Polla, id=polla_id)

    if polla.status == 'Paid':
        messages.warning(request, 'Esta polla ya fue pagada')
        return redirect('admin_panel:manage_pollas')

    if polla.status != 'Close':
        messages.error(request, 'Debes ingresar resultados primero')
        return redirect('admin_panel:enter_results_polla', polla_id=polla.id)

    if request.method == 'POST':
        from admin_panel.utils import process_polla_payment
        success = process_polla_payment(polla)

        if success:
            messages.success(request, 'Premios distribuidos exitosamente')
            return redirect('admin_panel:manage_pollas')
        else:
            messages.error(request, 'Error al procesar pagos')

    # Show winners and prize distribution
    from admin_panel.utils import get_polla_winners
    winners = get_polla_winners(polla)

    return render(request, 'admin_panel/pay_polla.html', {
        'title': f'Pagar Premios - {polla.code4}',
        'polla': polla,
        'winners': winners
    })


@admin_required
def pay_evento(request, evento_id):
    """Process prize payments for evento"""
    evento = get_object_or_404(Evento, id=evento_id)

    if evento.status == 'Paid':
        messages.warning(request, 'Este evento ya fue pagado')
        return redirect('admin_panel:manage_eventos')

    if evento.status != 'Close':
        messages.error(request, 'Debes ingresar resultados primero')
        return redirect('admin_panel:enter_results_evento', evento_id=evento.id)

    if request.method == 'POST':
        from admin_panel.utils import process_evento_payment
        success = process_evento_payment(evento)

        if success:
            messages.success(request, 'Premios distribuidos exitosamente')
            return redirect('admin_panel:manage_eventos')
        else:
            messages.error(request, 'Error al procesar pagos')

    # Show winners and prize distribution
    from admin_panel.utils import get_evento_winners
    winners = get_evento_winners(evento)

    return render(request, 'admin_panel/pay_evento.html', {
        'title': f'Pagar Premios - {evento.name}',
        'evento': evento,
        'winners': winners
    })


# ==================== USER MANAGEMENT ====================

@superadmin_required
def manage_users(request):
    """Manage users (superadmin only)"""
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin_panel/manage_users.html', {
        'title': 'Administrar Usuarios',
        'users': users
    })
