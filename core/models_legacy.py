"""
Legacy Models - Read-Only Access to PHP Tables

These models provide READ-ONLY access to the original PHP tables.
They are used ONLY for data migration purposes.

IMPORTANT:
- managed = False: Django will NOT create/modify these tables
- These tables are NEVER modified by Django
- Only used to READ data for migration to new core_ tables
"""

from django.db import models


class LegacyUser(models.Model):
    """Read-only access to legacy 'user' table"""
    idUser = models.AutoField(primary_key=True, db_column='idUser')
    email = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # Already bcrypt hashed

    class Meta:
        managed = False  # Django won't touch this table
        db_table = 'user'


class LegacyHipodromo(models.Model):
    """Read-only access to legacy 'hipodromo' table"""
    idHipodromo = models.AutoField(primary_key=True, db_column='idHipodromo')
    nombre = models.CharField(max_length=255)
    pais = models.CharField(max_length=100, blank=True)
    logo = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'hipodromo'


class LegacyLiga(models.Model):
    """Read-only access to legacy 'ligas' table"""
    idLigas = models.AutoField(primary_key=True, db_column='idLigas')
    name = models.CharField(max_length=255)
    pais = models.CharField(max_length=100, blank=True)
    logo = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'ligas'


class LegacyEquipo(models.Model):
    """Read-only access to legacy 'equipos' table"""
    idEquipo = models.AutoField(primary_key=True, db_column='idEquipo')
    idLiga = models.IntegerField(db_column='idLiga')
    nombre = models.CharField(max_length=255)
    logo = models.CharField(max_length=255, blank=True)
    pais = models.CharField(max_length=100, blank=True)

    class Meta:
        managed = False
        db_table = 'equipos'


class LegacyPolla(models.Model):
    """Read-only access to legacy 'pollas' table"""
    idPolla = models.AutoField(primary_key=True, db_column='idPolla')
    code4 = models.CharField(max_length=10)
    racetrack = models.CharField(max_length=255)
    date_race = models.DateTimeField()
    priceEntry = models.DecimalField(max_digits=10, decimal_places=2, db_column='priceEntry')

    f1 = models.IntegerField(null=True, blank=True)
    f2 = models.IntegerField(null=True, blank=True)
    f3 = models.IntegerField(null=True, blank=True)
    f4 = models.IntegerField(null=True, blank=True)
    f5 = models.IntegerField(null=True, blank=True)
    f6 = models.IntegerField(null=True, blank=True)

    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'pollas'


class LegacyEvento(models.Model):
    """Read-only access to legacy 'eventos' table"""
    idEvento = models.AutoField(primary_key=True, db_column='idEvento')
    code4 = models.CharField(max_length=10)
    idLiga = models.IntegerField(db_column='idLiga')
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    priceEntry = models.DecimalField(max_digits=10, decimal_places=2, db_column='priceEntry')
    tipo_juego = models.IntegerField(default=1)
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'eventos'


class LegacyEvPartido(models.Model):
    """Read-only access to legacy 'ev_partidos' table"""
    idPartido = models.AutoField(primary_key=True, db_column='idPartido')
    idEvento = models.IntegerField(db_column='idEvento')
    idEq1 = models.IntegerField(db_column='idEq1')
    idEq2 = models.IntegerField(db_column='idEq2')
    ordenPa = models.IntegerField(db_column='ordenPa')
    date = models.DateTimeField()
    scoreE1 = models.IntegerField(null=True, blank=True, db_column='scoreE1')
    scoreE2 = models.IntegerField(null=True, blank=True, db_column='scoreE2')

    class Meta:
        managed = False
        db_table = 'ev_partidos'


class LegacyBetPolla(models.Model):
    """Read-only access to legacy 'bets_pollas' table"""
    idBet = models.AutoField(primary_key=True, db_column='idBet')
    idUser = models.IntegerField(db_column='idUser')
    idPolla = models.IntegerField(db_column='idPolla')

    c1 = models.IntegerField()
    c2 = models.IntegerField()
    c3 = models.IntegerField()
    c4 = models.IntegerField()
    c5 = models.IntegerField()
    c6 = models.IntegerField()

    creditCost = models.DecimalField(max_digits=10, decimal_places=2, db_column='creditCost')
    date_bet = models.DateTimeField()
    ptoTot = models.IntegerField(default=0, db_column='ptoTot')
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'bets_pollas'


class LegacyBetEvento(models.Model):
    """Read-only access to legacy 'bets_eventos' table"""
    idBet = models.AutoField(primary_key=True, db_column='idBet')
    idUser = models.IntegerField(db_column='idUser')
    idEvento = models.IntegerField(db_column='idEvento')
    creditCost = models.DecimalField(max_digits=10, decimal_places=2, db_column='creditCost')
    date_bet = models.DateTimeField()
    puntos = models.IntegerField(default=0)
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'bets_eventos'


class LegacyBetEvPartido(models.Model):
    """Read-only access to legacy 'bets_ev_partidos' table"""
    id = models.AutoField(primary_key=True)
    idBet = models.IntegerField(db_column='idBet')
    idPartido = models.IntegerField(db_column='idPartido')
    scoreE1 = models.IntegerField(db_column='scoreE1')
    scoreE2 = models.IntegerField(db_column='scoreE2')
    puntos = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'bets_ev_partidos'


class LegacyCtaCash(models.Model):
    """Read-only access to legacy 'ctaCash' table"""
    idCash = models.AutoField(primary_key=True, db_column='idCash')
    idUser = models.IntegerField(db_column='idUser')
    idPolla = models.IntegerField(null=True, blank=True, db_column='idPolla')
    idBet = models.IntegerField(null=True, blank=True, db_column='idBet')
    trxDate = models.DateTimeField(db_column='trxDate')
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    comment = models.TextField(blank=True)
    tipo = models.CharField(max_length=50)
    conciliado = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'ctaCash'


class LegacyEvCtaCash(models.Model):
    """Read-only access to legacy 'ev_ctaCash' table"""
    idCash = models.AutoField(primary_key=True, db_column='idCash')
    idUser = models.IntegerField(db_column='idUser')
    idEvento = models.IntegerField(null=True, blank=True, db_column='idEvento')
    idBet = models.IntegerField(null=True, blank=True, db_column='idBet')
    trxDate = models.DateTimeField(db_column='trxDate')
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    comment = models.TextField(blank=True)
    tipo = models.CharField(max_length=50)
    conciliado = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'ev_ctaCash'


class LegacyJornada5y6(models.Model):
    """Read-only access to legacy 'jornadas_5y6' table"""
    id = models.AutoField(primary_key=True)
    hipodromo = models.CharField(max_length=255)
    fecha = models.DateField()
    fecha_creacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'jornadas_5y6'


class LegacyCuadro5y6(models.Model):
    """Read-only access to legacy 'cuadros_5y6' table"""
    id = models.AutoField(primary_key=True)
    id_jornada = models.IntegerField()
    nombre_cuadro = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'cuadros_5y6'


class LegacySeleccion5y6(models.Model):
    """Read-only access to legacy 'selecciones_5y6' table"""
    id = models.AutoField(primary_key=True)
    id_cuadro = models.IntegerField()
    numero_carrera = models.IntegerField()
    numero_caballo = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'selecciones_5y6'


class LegacyGanador5y6(models.Model):
    """Read-only access to legacy 'ganadores_5y6' table"""
    id = models.AutoField(primary_key=True)
    id_jornada = models.IntegerField()
    numero_carrera = models.IntegerField()
    numero_caballo = models.IntegerField()
    fecha_registro = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'ganadores_5y6'
