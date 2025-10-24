"""
Admin Panel Utility Functions

These replicate the business logic from PHP's func.php:
- Prize calculation
- Winner determination
- Prize distribution
- Email notifications
"""
from decimal import Decimal
from django.db.models import Sum, Count
from django.utils import timezone
from core.models import AccountTransaction, EventTransaction, BetPolla, BetEvento


def get_polla_winners(polla):
    """
    Calculate winners for a polla (replicates PHP's getPremiosbyPolla)
    Returns list of winners with prize amounts
    """
    # Get all bets ordered by points
    bets = polla.bets.all().order_by('-pto_tot', 'date_bet')

    if not bets.exists():
        return []

    # Calculate total pot
    total_pot = AccountTransaction.objects.filter(
        polla=polla,
        tipo='Pote'
    ).aggregate(total=Sum('qty'))['total'] or Decimal('0.00')

    num_participants = bets.count()

    # Prize distribution based on participant count (matches PHP logic)
    if num_participants < 50:
        # Top 2 places
        first_place_pct = Decimal('0.70')
        second_place_pct = Decimal('0.30')
        num_winners = min(2, num_participants)
    else:
        # Top 3 places
        first_place_pct = Decimal('0.60')
        second_place_pct = Decimal('0.25')
        third_place_pct = Decimal('0.15')
        num_winners = min(3, num_participants)

    # Determine winners
    winners = []
    top_bets = list(bets[:num_winners])

    for i, bet in enumerate(top_bets):
        if i == 0:
            pct = first_place_pct
            place = '1er Lugar'
        elif i == 1:
            pct = second_place_pct
            place = '2do Lugar'
        else:
            pct = third_place_pct
            place = '3er Lugar'

        # Check for ties
        tied_bets = [b for b in top_bets if b.pto_tot == bet.pto_tot]
        if len(tied_bets) > 1:
            # Split prize among tied participants
            prize = (total_pot * pct) / len(tied_bets)
        else:
            prize = total_pot * pct

        winners.append({
            'user': bet.user,
            'bet': bet,
            'points': bet.pto_tot,
            'place': place,
            'prize': round(prize, 2)
        })

    return winners


def process_polla_payment(polla):
    """
    Process prize payments for a polla (replicates PHP's tblPagarPollas)
    Returns True if successful
    """
    if polla.status == 'Paid':
        return False

    winners = get_polla_winners(polla)
    now = timezone.now()

    for winner_data in winners:
        user = winner_data['user']
        prize = winner_data['prize']

        # Credit user's account
        AccountTransaction.objects.create(
            user=user,
            polla=polla,
            bet=winner_data['bet'],
            tipo='Premio',
            comment=f"Premio {winner_data['place']} - {polla.code4}",
            qty=prize,
            trx_date=now
        )

        # Debit from pot
        AccountTransaction.objects.create(
            user_id=1,  # System user
            polla=polla,
            tipo='Pote',
            comment=f"Premio pagado {winner_data['place']} - {polla.code4}",
            qty=-prize,
            trx_date=now
        )

        # Send email notification
        send_winner_email_polla(user, polla, prize, winner_data['place'])

    # Mark as paid
    polla.status = 'Paid'
    polla.save()

    return True


def get_evento_winners(evento):
    """
    Calculate winners for an evento (replicates PHP's getPremiosbyEvento)
    Returns list of winners with prize amounts
    """
    # Get all bets ordered by points
    bets = evento.bets.all().order_by('-puntos', 'date_bet')

    if not bets.exists():
        return []

    # Calculate total pot
    total_pot = EventTransaction.objects.filter(
        evento=evento,
        tipo='Pote'
    ).aggregate(total=Sum('qty'))['total'] or Decimal('0.00')

    num_participants = bets.count()

    # Prize distribution (same logic as pollas)
    if num_participants < 50:
        first_place_pct = Decimal('0.70')
        second_place_pct = Decimal('0.30')
        num_winners = min(2, num_participants)
    else:
        first_place_pct = Decimal('0.60')
        second_place_pct = Decimal('0.25')
        third_place_pct = Decimal('0.15')
        num_winners = min(3, num_participants)

    winners = []
    top_bets = list(bets[:num_winners])

    for i, bet in enumerate(top_bets):
        if i == 0:
            pct = first_place_pct
            place = '1er Lugar'
        elif i == 1:
            pct = second_place_pct
            place = '2do Lugar'
        else:
            pct = third_place_pct
            place = '3er Lugar'

        tied_bets = [b for b in top_bets if b.puntos == bet.puntos]
        if len(tied_bets) > 1:
            prize = (total_pot * pct) / len(tied_bets)
        else:
            prize = total_pot * pct

        winners.append({
            'user': bet.user,
            'bet': bet,
            'points': bet.puntos,
            'place': place,
            'prize': round(prize, 2)
        })

    return winners


def process_evento_payment(evento):
    """
    Process prize payments for an evento (replicates PHP's tblPagarEvento)
    Returns True if successful
    """
    if evento.status == 'Paid':
        return False

    winners = get_evento_winners(evento)
    now = timezone.now()

    for winner_data in winners:
        user = winner_data['user']
        prize = winner_data['prize']

        # Credit user's account
        EventTransaction.objects.create(
            user=user,
            evento=evento,
            bet=winner_data['bet'],
            tipo='Premio',
            comment=f"Premio {winner_data['place']} - {evento.name}",
            qty=prize,
            trx_date=now
        )

        # Debit from pot
        EventTransaction.objects.create(
            user_id=1,  # System user
            evento=evento,
            tipo='Pote',
            comment=f"Premio pagado {winner_data['place']} - {evento.name}",
            qty=-prize,
            trx_date=now
        )

        # Send email notification
        send_winner_email_evento(user, evento, prize, winner_data['place'])

    # Mark as paid
    evento.status = 'Paid'
    evento.save()

    return True


def calculate_evento_points(evento):
    """
    Calculate points for all evento bets based on match results
    (Replicates PHP's calcularPuntosEvento)
    """
    for bet in evento.bets.all():
        total_points = 0

        for prediction in bet.match_predictions.all():
            match = prediction.match

            if match.score_team1 is None or match.score_team2 is None:
                continue  # Results not entered yet

            # Scoring logic varies by tipo_juego
            if evento.tipo_juego == 3:
                # NFL - Winner selection
                actual_winner = 'E1' if match.score_team1 > match.score_team2 else 'E2'
                predicted_winner = 'E1' if prediction.score_team1 > prediction.score_team2 else 'E2'

                if actual_winner == predicted_winner:
                    points = 1
                else:
                    points = 0

            elif evento.tipo_juego in [5, 6]:
                # Soccer - Winner or Tie
                if match.score_team1 == match.score_team2:
                    actual_result = 'TIE'
                elif match.score_team1 > match.score_team2:
                    actual_result = 'E1'
                else:
                    actual_result = 'E2'

                if prediction.score_team1 == prediction.score_team2:
                    predicted_result = 'TIE'
                elif prediction.score_team1 > prediction.score_team2:
                    predicted_result = 'E1'
                else:
                    predicted_result = 'E2'

                if actual_result == predicted_result:
                    points = 1
                else:
                    points = 0

            else:
                # Exact score prediction
                if (prediction.score_team1 == match.score_team1 and
                        prediction.score_team2 == match.score_team2):
                    points = 3  # Exact match
                elif ((prediction.score_team1 > prediction.score_team2 and
                       match.score_team1 > match.score_team2) or
                      (prediction.score_team1 < prediction.score_team2 and
                       match.score_team1 < match.score_team2) or
                      (prediction.score_team1 == prediction.score_team2 and
                       match.score_team1 == match.score_team2)):
                    points = 1  # Correct winner/tie
                else:
                    points = 0

            prediction.puntos = points
            prediction.save()
            total_points += points

        bet.puntos = total_points
        bet.save()


def send_winner_email_polla(user, polla, prize, place):
    """Send email notification to polla winner"""
    from django.core.mail import send_mail
    from django.conf import settings

    subject = f'Ganaste la polla de {polla.racetrack.nombre}!'
    message = f"""
    Felicitaciones {user.alias}:

    Has ganado {place} en la polla {polla.code4} - {polla.racetrack.nombre}
    Se ha acreditado USD ${prize} a tu cuenta.

    Sigue jugando, Suerte y Gaceta!

    - La Polla - ElGuaire
    """

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email to {user.email}: {e}")


def send_winner_email_evento(user, evento, prize, place):
    """Send email notification to evento winner"""
    from django.core.mail import send_mail
    from django.conf import settings

    subject = f'Ganaste el evento {evento.name}!'
    message = f"""
    Felicitaciones {user.alias}:

    Has ganado {place} en el evento {evento.code4} - {evento.name}
    Se ha acreditado USD ${prize} a tu cuenta.

    Sigue jugando, Suerte!

    - La Polla - ElGuaire
    """

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email to {user.email}: {e}")
