"""
Core Django Models for Betting Platform

These models create NEW tables in the database (with 'core_' prefix).
The legacy PHP tables remain UNTOUCHED for safety.

Table mapping:
Legacy Table      -> New Django Table
user              -> core_user
pollas            -> core_polla
eventos           -> core_evento
equipos           -> core_team
ligas             -> core_league
hipodromo         -> core_racetrack
ev_partidos       -> core_match
bets_pollas       -> core_betpolla
bets_eventos      -> core_betevento
bets_ev_partidos  -> core_betmatch
ctaCash           -> core_accounttransaction
ev_ctaCash        -> core_eventtransaction
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from decimal import Decimal


# ==================== USER MODELS ====================

class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""

    def create_user(self, email, alias, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not alias:
            raise ValueError('Users must have an alias')

        email = self.normalize_email(email)
        user = self.model(email=email, alias=alias, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, alias, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superadmin', True)

        return self.create_user(email, alias, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model (creates table: core_user)
    Maps to legacy 'user' table
    """
    email = models.EmailField(unique=True, max_length=255)
    alias = models.CharField(max_length=255)

    # Permission flags (custom, not Django's default)
    is_admin = models.BooleanField(default=False, help_text='Can access /adm/ area')
    is_superadmin = models.BooleanField(default=False, help_text='Full admin access')

    # Django required fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # For Django admin access (optional)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['alias']

    class Meta:
        db_table = 'core_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.alias} ({self.email})"

    def get_balance(self):
        """Calculate user's total balance from both transaction tables"""
        polla_balance = AccountTransaction.objects.filter(
            user=self,
            conciliado=False
        ).aggregate(total=models.Sum('qty'))['total'] or Decimal('0.00')

        event_balance = EventTransaction.objects.filter(
            user=self,
            conciliado=False
        ).aggregate(total=models.Sum('qty'))['total'] or Decimal('0.00')

        return polla_balance + event_balance


# ==================== REFERENCE DATA MODELS ====================

class Racetrack(models.Model):
    """
    Racetrack/Hipódromo model (creates table: core_racetrack)
    Maps to legacy 'hipodromo' table
    """
    nombre = models.CharField(max_length=255)
    pais = models.CharField(max_length=100, blank=True)
    logo = models.CharField(max_length=255, blank=True, help_text='Logo filename')

    class Meta:
        db_table = 'core_racetrack'
        verbose_name = 'Racetrack'
        verbose_name_plural = 'Racetracks'

    def __str__(self):
        return self.nombre


class League(models.Model):
    """
    League/Competition model (creates table: core_league)
    Maps to legacy 'ligas' table
    """
    name = models.CharField(max_length=255)
    pais = models.CharField(max_length=100, blank=True)
    logo = models.CharField(max_length=255, blank=True, help_text='Logo filename')

    class Meta:
        db_table = 'core_league'
        verbose_name = 'League'
        verbose_name_plural = 'Leagues'

    def __str__(self):
        return self.name


class Team(models.Model):
    """
    Team model (creates table: core_team)
    Maps to legacy 'equipos' table
    """
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='teams')
    nombre = models.CharField(max_length=255)
    logo = models.CharField(max_length=255, blank=True, help_text='Logo filename')
    pais = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'core_team'
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ==================== BETTING EVENT MODELS ====================

class Polla(models.Model):
    """
    Horse Racing Pool model (creates table: core_polla)
    Maps to legacy 'pollas' table
    """
    STATUS_CHOICES = [
        ('Running', 'Running'),
        ('Close', 'Close'),
        ('Paid', 'Paid'),
    ]

    code4 = models.CharField(max_length=10, unique=True)
    racetrack = models.ForeignKey(Racetrack, on_delete=models.CASCADE, related_name='pollas')
    date_race = models.DateTimeField()
    price_entry = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('2.00'))

    # Winning horse numbers (1-20)
    f1 = models.IntegerField(null=True, blank=True, help_text='Race 1 winner')
    f2 = models.IntegerField(null=True, blank=True, help_text='Race 2 winner')
    f3 = models.IntegerField(null=True, blank=True, help_text='Race 3 winner')
    f4 = models.IntegerField(null=True, blank=True, help_text='Race 4 winner')
    f5 = models.IntegerField(null=True, blank=True, help_text='Race 5 winner')
    f6 = models.IntegerField(null=True, blank=True, help_text='Race 6 winner')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Running')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_polla'
        verbose_name = 'Polla (Horse Race Pool)'
        verbose_name_plural = 'Pollas'
        ordering = ['-date_race']

    def __str__(self):
        return f"{self.code4} - {self.racetrack.nombre}"

    def is_open(self):
        """Check if betting is still open"""
        return self.status == 'Running' and self.date_race > timezone.now()

    def is_paid(self):
        """Check if prizes have been distributed"""
        return self.status == 'Paid'


class Evento(models.Model):
    """
    Sports Event model (creates table: core_evento)
    Maps to legacy 'eventos' table
    """
    STATUS_CHOICES = [
        ('Running', 'Running'),
        ('Close', 'Close'),
        ('Paid', 'Paid'),
    ]

    code4 = models.CharField(max_length=10, unique=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='eventos')
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    price_entry = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('2.00'))

    tipo_juego = models.IntegerField(
        default=1,
        help_text='1=Scores, 3=NFL Winner, 5/6=Soccer Winner/Tie'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Running')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_evento'
        verbose_name = 'Evento (Sports Event)'
        verbose_name_plural = 'Eventos'
        ordering = ['-date']

    def __str__(self):
        return f"{self.code4} - {self.name}"

    def is_open(self):
        """Check if betting is still open"""
        return self.status == 'Running'

    def is_updatable(self):
        """Check if bets can be updated"""
        # Can update until first match starts
        first_match = self.matches.order_by('date').first()
        if first_match:
            return timezone.now() < first_match.date
        return self.is_open()


class Match(models.Model):
    """
    Individual match within an evento (creates table: core_match)
    Maps to legacy 'ev_partidos' table
    """
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='matches')
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team2')

    orden_pa = models.IntegerField(help_text='Match order in event')
    date = models.DateTimeField()

    # Actual results (filled by admin)
    score_team1 = models.IntegerField(null=True, blank=True)
    score_team2 = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'core_match'
        verbose_name = 'Match'
        verbose_name_plural = 'Matches'
        ordering = ['evento', 'orden_pa']

    def __str__(self):
        return f"{self.team1.nombre} vs {self.team2.nombre}"


# ==================== BET MODELS ====================

class BetPolla(models.Model):
    """
    User's horse race bet (creates table: core_betpolla)
    Maps to legacy 'bets_pollas' table
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='polla_bets')
    polla = models.ForeignKey(Polla, on_delete=models.CASCADE, related_name='bets')

    # User's horse selections (1-20)
    c1 = models.IntegerField(help_text='Race 1 selection')
    c2 = models.IntegerField(help_text='Race 2 selection')
    c3 = models.IntegerField(help_text='Race 3 selection')
    c4 = models.IntegerField(help_text='Race 4 selection')
    c5 = models.IntegerField(help_text='Race 5 selection')
    c6 = models.IntegerField(help_text='Race 6 selection')

    credit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    date_bet = models.DateTimeField(auto_now_add=True)

    # Scoring
    pto_tot = models.IntegerField(default=0, help_text='Total points earned')

    status = models.CharField(max_length=20, default='ok')

    class Meta:
        db_table = 'core_betpolla'
        verbose_name = 'Polla Bet'
        verbose_name_plural = 'Polla Bets'
        unique_together = ['user', 'polla']  # One bet per user per polla

    def __str__(self):
        return f"{self.user.alias} - {self.polla.code4}"

    def calculate_points(self):
        """Calculate points based on correct predictions"""
        points = 0
        if self.polla.f1 and self.c1 == self.polla.f1:
            points += 1
        if self.polla.f2 and self.c2 == self.polla.f2:
            points += 1
        if self.polla.f3 and self.c3 == self.polla.f3:
            points += 1
        if self.polla.f4 and self.c4 == self.polla.f4:
            points += 1
        if self.polla.f5 and self.c5 == self.polla.f5:
            points += 1
        if self.polla.f6 and self.c6 == self.polla.f6:
            points += 1

        self.pto_tot = points
        self.save()
        return points


class BetEvento(models.Model):
    """
    User's sports event bet (creates table: core_betevento)
    Maps to legacy 'bets_eventos' table
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evento_bets')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='bets')

    credit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    date_bet = models.DateTimeField(auto_now_add=True)

    # Scoring
    puntos = models.IntegerField(default=0, help_text='Total points earned')

    status = models.CharField(max_length=20, default='ok')

    class Meta:
        db_table = 'core_betevento'
        verbose_name = 'Evento Bet'
        verbose_name_plural = 'Evento Bets'
        unique_together = ['user', 'evento']

    def __str__(self):
        return f"{self.user.alias} - {self.evento.code4}"


class BetMatch(models.Model):
    """
    User's prediction for individual match (creates table: core_betmatch)
    Maps to legacy 'bets_ev_partidos' table
    """
    bet_evento = models.ForeignKey(BetEvento, on_delete=models.CASCADE, related_name='match_predictions')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='predictions')

    # User's predictions
    score_team1 = models.IntegerField()
    score_team2 = models.IntegerField()

    # Points earned for this match
    puntos = models.IntegerField(default=0)

    class Meta:
        db_table = 'core_betmatch'
        verbose_name = 'Match Prediction'
        verbose_name_plural = 'Match Predictions'

    def __str__(self):
        return f"{self.bet_evento.user.alias} - {self.match}"


# ==================== TRANSACTION MODELS ====================

class AccountTransaction(models.Model):
    """
    Transaction for pollas (creates table: core_accounttransaction)
    Maps to legacy 'ctaCash' table
    """
    TIPO_CHOICES = [
        ('Apuesta', 'Apuesta'),
        ('Premio', 'Premio'),
        ('Comision', 'Comision'),
        ('Pote', 'Pote'),
        ('Acumulado2305', 'Acumulado2305'),
        ('AcumuladoRecord2022', 'AcumuladoRecord2022'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='account_transactions')
    polla = models.ForeignKey(Polla, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    bet = models.ForeignKey(BetPolla, on_delete=models.CASCADE, null=True, blank=True, related_name='transactions')

    trx_date = models.DateTimeField(default=timezone.now)
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    comment = models.TextField(blank=True)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    conciliado = models.BooleanField(default=False)

    class Meta:
        db_table = 'core_accounttransaction'
        verbose_name = 'Account Transaction'
        verbose_name_plural = 'Account Transactions'
        ordering = ['-trx_date']

    def __str__(self):
        return f"{self.user.alias} - {self.tipo} - ${self.qty}"


class EventTransaction(models.Model):
    """
    Transaction for eventos (creates table: core_eventtransaction)
    Maps to legacy 'ev_ctaCash' table
    """
    TIPO_CHOICES = [
        ('Apuesta', 'Apuesta'),
        ('Premio', 'Premio'),
        ('Comision', 'Comision'),
        ('Pote', 'Pote'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_transactions')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    bet = models.ForeignKey(BetEvento, on_delete=models.CASCADE, null=True, blank=True, related_name='transactions')

    trx_date = models.DateTimeField(default=timezone.now)
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    comment = models.TextField(blank=True)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    conciliado = models.BooleanField(default=False)

    class Meta:
        db_table = 'core_eventtransaction'
        verbose_name = 'Event Transaction'
        verbose_name_plural = 'Event Transactions'
        ordering = ['-trx_date']

    def __str__(self):
        return f"{self.user.alias} - {self.tipo} - ${self.qty}"


# ==================== 5Y6 SYSTEM MODELS ====================

class Jornada5y6(models.Model):
    """5y6 Racing day"""
    hipodromo = models.CharField(max_length=255)
    fecha = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_jornada5y6'
        verbose_name = 'Jornada 5y6'
        verbose_name_plural = 'Jornadas 5y6'

    def __str__(self):
        return f"{self.hipodromo} - {self.fecha}"


class Cuadro5y6(models.Model):
    """5y6 Grid/Card"""
    jornada = models.ForeignKey(Jornada5y6, on_delete=models.CASCADE, related_name='cuadros')
    nombre_cuadro = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_cuadro5y6'
        verbose_name = 'Cuadro 5y6'
        verbose_name_plural = 'Cuadros 5y6'

    def __str__(self):
        return f"{self.nombre_cuadro} - {self.jornada}"


class Seleccion5y6(models.Model):
    """5y6 Horse selection"""
    cuadro = models.ForeignKey(Cuadro5y6, on_delete=models.CASCADE, related_name='selecciones')
    numero_carrera = models.IntegerField(help_text='Race number (1-6)')
    numero_caballo = models.IntegerField(help_text='Horse number (1-20)')

    class Meta:
        db_table = 'core_seleccion5y6'
        verbose_name = 'Selección 5y6'
        verbose_name_plural = 'Selecciones 5y6'

    def __str__(self):
        return f"Race {self.numero_carrera} - Horse {self.numero_caballo}"


class Ganador5y6(models.Model):
    """5y6 Winning horses"""
    jornada = models.ForeignKey(Jornada5y6, on_delete=models.CASCADE, related_name='ganadores')
    numero_carrera = models.IntegerField(help_text='Race number (1-6)')
    numero_caballo = models.IntegerField(help_text='Winning horse (1-20)')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_ganador5y6'
        verbose_name = 'Ganador 5y6'
        verbose_name_plural = 'Ganadores 5y6'
        unique_together = ['jornada', 'numero_carrera']

    def __str__(self):
        return f"Race {self.numero_carrera} - Winner: {self.numero_caballo}"
