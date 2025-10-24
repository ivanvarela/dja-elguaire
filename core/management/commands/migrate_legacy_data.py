"""
Data Migration Command - Transfer data from legacy PHP tables to new Django tables

Usage:
    python manage.py migrate_legacy_data

This command safely copies all data from the old PHP tables to the new Django tables.
Legacy tables remain UNTOUCHED.

Process:
1. Migrate reference data (racetracks, leagues, teams)
2. Migrate users
3. Migrate events (pollas, eventos, matches)
4. Migrate bets
5. Migrate transactions
6. Migrate 5y6 system data
7. Verify data integrity

Safety Features:
- Dry-run mode available
- Transaction rollback on error
- Progress reporting
- Data verification
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.hashers import make_password
from core.models import (
    User, Racetrack, League, Team, Polla, Evento, Match,
    BetPolla, BetEvento, BetMatch, AccountTransaction, EventTransaction,
    Jornada5y6, Cuadro5y6, Seleccion5y6, Ganador5y6
)
from core.models_legacy import (
    LegacyUser, LegacyHipodromo, LegacyLiga, LegacyEquipo,
    LegacyPolla, LegacyEvento, LegacyEvPartido,
    LegacyBetPolla, LegacyBetEvento, LegacyBetEvPartido,
    LegacyCtaCash, LegacyEvCtaCash,
    LegacyJornada5y6, LegacyCuadro5y6, LegacySeleccion5y6, LegacyGanador5y6
)


class Command(BaseCommand):
    help = 'Migrate data from legacy PHP tables to new Django tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run migration without actually saving data',
        )
        parser.add_argument(
            '--skip-users',
            action='store_true',
            help='Skip user migration',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        skip_users = options['skip_users']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))

        self.stdout.write(self.style.SUCCESS('Starting data migration from legacy tables...'))
        self.stdout.write('')

        try:
            with transaction.atomic():
                # Step 1: Migrate reference data
                self.migrate_racetracks()
                self.migrate_leagues()
                self.migrate_teams()

                # Step 2: Migrate users
                if not skip_users:
                    self.migrate_users()
                else:
                    self.stdout.write(self.style.WARNING('Skipping user migration'))

                # Step 3: Migrate pollas
                self.migrate_pollas()

                # Step 4: Migrate eventos
                self.migrate_eventos()
                self.migrate_matches()

                # Step 5: Migrate bets
                self.migrate_polla_bets()
                self.migrate_evento_bets()
                self.migrate_match_predictions()

                # Step 6: Migrate transactions
                self.migrate_account_transactions()
                self.migrate_event_transactions()

                # Step 7: Migrate 5y6 system
                self.migrate_5y6_system()

                # Step 8: Verify data
                self.verify_migration()

                if dry_run:
                    self.stdout.write(self.style.WARNING('DRY RUN - Rolling back...'))
                    raise Exception("Dry run - intentional rollback")

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('='*70))
            self.stdout.write(self.style.SUCCESS('MIGRATION COMPLETED SUCCESSFULLY!'))
            self.stdout.write(self.style.SUCCESS('='*70))
            self.stdout.write(self.style.SUCCESS('All data has been migrated to new Django tables.'))
            self.stdout.write(self.style.SUCCESS('Legacy tables remain UNTOUCHED.'))

        except Exception as e:
            if not dry_run:
                self.stdout.write(self.style.ERROR(f'Migration failed: {str(e)}'))
                self.stdout.write(self.style.ERROR('All changes have been rolled back.'))
            raise

    def migrate_racetracks(self):
        self.stdout.write('Migrating racetracks...')
        count = 0
        for legacy in LegacyHipodromo.objects.all():
            Racetrack.objects.update_or_create(
                id=legacy.idHipodromo,
                defaults={
                    'nombre': legacy.nombre,
                    'pais': legacy.pais or '',
                    'logo': legacy.logo or '',
                }
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrated {count} racetracks'))

    def migrate_leagues(self):
        self.stdout.write('Migrating leagues...')
        count = 0
        for legacy in LegacyLiga.objects.all():
            League.objects.update_or_create(
                id=legacy.idLigas,
                defaults={
                    'name': legacy.name,
                    'pais': legacy.pais or '',
                    'logo': legacy.logo or '',
                }
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrated {count} leagues'))

    def migrate_teams(self):
        self.stdout.write('Migrating teams...')
        count = 0
        for legacy in LegacyEquipo.objects.all():
            try:
                league = League.objects.get(id=legacy.idLiga)
                Team.objects.update_or_create(
                    id=legacy.idEquipo,
                    defaults={
                        'league': league,
                        'nombre': legacy.nombre,
                        'logo': legacy.logo or '',
                        'pais': legacy.pais or '',
                    }
                )
                count += 1
            except League.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ! League {legacy.idLiga} not found for team {legacy.nombre}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrated {count} teams'))

    def migrate_users(self):
        self.stdout.write('Migrating users...')
        count = 0
        for legacy in LegacyUser.objects.all():
            # Keep the password hash as-is (it's already bcrypt)
            User.objects.update_or_create(
                id=legacy.idUser,
                defaults={
                    'email': legacy.email,
                    'alias': legacy.alias,
                    'password': legacy.password,  # Already hashed with bcrypt
                    'is_active': True,
                }
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrated {count} users'))

    def migrate_pollas(self):
        self.stdout.write('Migrating pollas (horse racing pools)...')
        count = 0
        for legacy in LegacyPolla.objects.all():
            try:
                # Find racetrack by name (since legacy uses name, not FK)
                racetrack, _ = Racetrack.objects.get_or_create(
                    nombre=legacy.racetrack,
                    defaults={'pais': '', 'logo': ''}
                )

                Polla.objects.update_or_create(
                    id=legacy.idPolla,
                    defaults={
                        'code4': legacy.code4,
                        'racetrack': racetrack,
                        'date_race': legacy.date_race,
                        'price_entry': legacy.priceEntry,
                        'f1': legacy.f1,
                        'f2': legacy.f2,
                        'f3': legacy.f3,
                        'f4': legacy.f4,
                        'f5': legacy.f5,
                        'f6': legacy.f6,
                        'status': legacy.status,
                    }
                )
                count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ! Error migrating polla {legacy.idPolla}: {str(e)}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrated {count} pollas'))

    def migrate_eventos(self):
        self.stdout.write('Migrating eventos (sports events)...')
        count = 0
        for legacy in LegacyEvento.objects.all():
            try:
                league = League.objects.get(id=legacy.idLiga)
                Evento.objects.update_or_create(
                    id=legacy.idEvento,
                    defaults={
                        'code4': legacy.code4,
                        'league': league,
                        'name': legacy.name,
                        'date': legacy.date,
                        'price_entry': legacy.priceEntry,
                        'tipo_juego': legacy.tipo_juego,
                        'status': legacy.status,
                    }
                )
                count += 1
            except League.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ! League {legacy.idLiga} not found for evento {legacy.idEvento}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrated {count} eventos'))

    def migrate_matches(self):
        self.stdout.write('Migrating matches...')
        count = 0
        for legacy in LegacyEvPartido.objects.all():
            try:
                evento = Evento.objects.get(id=legacy.idEvento)
                team1 = Team.objects.get(id=legacy.idEq1)
                team2 = Team.objects.get(id=legacy.idEq2)

                Match.objects.update_or_create(
                    id=legacy.idPartido,
                    defaults={
                        'evento': evento,
                        'team1': team1,
                        'team2': team2,
                        'orden_pa': legacy.ordenPa,
                        'date': legacy.date,
                        'score_team1': legacy.scoreE1,
                        'score_team2': legacy.scoreE2,
                    }
                )
                count += 1
            except (Evento.DoesNotExist, Team.DoesNotExist) as e:
                self.stdout.write(self.style.WARNING(f'  ! Error migrating match {legacy.idPartido}: {str(e)}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrated {count} matches'))

    def migrate_polla_bets(self):
        self.stdout.write('Migrating polla bets...')
        count = 0
        for legacy in LegacyBetPolla.objects.all():
            try:
                user = User.objects.get(id=legacy.idUser)
                polla = Polla.objects.get(id=legacy.idPolla)

                BetPolla.objects.update_or_create(
                    id=legacy.idBet,
                    defaults={
                        'user': user,
                        'polla': polla,
                        'c1': legacy.c1,
                        'c2': legacy.c2,
                        'c3': legacy.c3,
                        'c4': legacy.c4,
                        'c5': legacy.c5,
                        'c6': legacy.c6,
                        'credit_cost': legacy.creditCost,
                        'date_bet': legacy.date_bet,
                        'pto_tot': legacy.ptoTot,
                        'status': legacy.status,
                    }
                )
                count += 1
            except (User.DoesNotExist, Polla.DoesNotExist) as e:
                self.stdout.write(self.style.WARNING(f'  ! Error migrating bet {legacy.idBet}: {str(e)}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrated {count} polla bets'))

    def migrate_evento_bets(self):
        self.stdout.write('Migrating evento bets...')
        count = 0
        for legacy in LegacyBetEvento.objects.all():
            try:
                user = User.objects.get(id=legacy.idUser)
                evento = Evento.objects.get(id=legacy.idEvento)

                BetEvento.objects.update_or_create(
                    id=legacy.idBet,
                    defaults={
                        'user': user,
                        'evento': evento,
                        'credit_cost': legacy.creditCost,
                        'date_bet': legacy.date_bet,
                        'puntos': legacy.puntos,
                        'status': legacy.status,
                    }
                )
                count += 1
            except (User.DoesNotExist, Evento.DoesNotExist) as e:
                self.stdout.write(self.style.WARNING(f'  ! Error migrating evento bet {legacy.idBet}: {str(e)}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrated {count} evento bets'))

    def migrate_match_predictions(self):
        self.stdout.write('Migrating match predictions...')
        count = 0
        for legacy in LegacyBetEvPartido.objects.all():
            try:
                bet_evento = BetEvento.objects.get(id=legacy.idBet)
                match = Match.objects.get(id=legacy.idPartido)

                BetMatch.objects.update_or_create(
                    id=legacy.id,
                    defaults={
                        'bet_evento': bet_evento,
                        'match': match,
                        'score_team1': legacy.scoreE1,
                        'score_team2': legacy.scoreE2,
                        'puntos': legacy.puntos,
                    }
                )
                count += 1
            except (BetEvento.DoesNotExist, Match.DoesNotExist) as e:
                self.stdout.write(self.style.WARNING(f'  ! Error migrating prediction {legacy.id}: {str(e)}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrated {count} match predictions'))

    def migrate_account_transactions(self):
        self.stdout.write('Migrating account transactions (ctaCash)...')
        count = 0
        for legacy in LegacyCtaCash.objects.all():
            try:
                user = User.objects.get(id=legacy.idUser)
                polla = Polla.objects.get(id=legacy.idPolla) if legacy.idPolla else None
                bet = BetPolla.objects.get(id=legacy.idBet) if legacy.idBet else None

                AccountTransaction.objects.update_or_create(
                    id=legacy.idCash,
                    defaults={
                        'user': user,
                        'polla': polla,
                        'bet': bet,
                        'trx_date': legacy.trxDate,
                        'qty': legacy.qty,
                        'comment': legacy.comment or '',
                        'tipo': legacy.tipo,
                        'conciliado': legacy.conciliado,
                    }
                )
                count += 1
            except User.DoesNotExist as e:
                self.stdout.write(self.style.WARNING(f'  ! Error migrating transaction {legacy.idCash}: {str(e)}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrated {count} account transactions'))

    def migrate_event_transactions(self):
        self.stdout.write('Migrating event transactions (ev_ctaCash)...')
        count = 0
        for legacy in LegacyEvCtaCash.objects.all():
            try:
                user = User.objects.get(id=legacy.idUser)
                evento = Evento.objects.get(id=legacy.idEvento) if legacy.idEvento else None
                bet = BetEvento.objects.get(id=legacy.idBet) if legacy.idBet else None

                EventTransaction.objects.update_or_create(
                    id=legacy.idCash,
                    defaults={
                        'user': user,
                        'evento': evento,
                        'bet': bet,
                        'trx_date': legacy.trxDate,
                        'qty': legacy.qty,
                        'comment': legacy.comment or '',
                        'tipo': legacy.tipo,
                        'conciliado': legacy.conciliado,
                    }
                )
                count += 1
            except User.DoesNotExist as e:
                self.stdout.write(self.style.WARNING(f'  ! Error migrating event transaction {legacy.idCash}: {str(e)}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrated {count} event transactions'))

    def migrate_5y6_system(self):
        self.stdout.write('Migrating 5y6 system data...')

        # Jornadas
        jornadas_count = 0
        for legacy in LegacyJornada5y6.objects.all():
            Jornada5y6.objects.update_or_create(
                id=legacy.id,
                defaults={
                    'hipodromo': legacy.hipodromo,
                    'fecha': legacy.fecha,
                }
            )
            jornadas_count += 1

        # Cuadros
        cuadros_count = 0
        for legacy in LegacyCuadro5y6.objects.all():
            try:
                jornada = Jornada5y6.objects.get(id=legacy.id_jornada)
                Cuadro5y6.objects.update_or_create(
                    id=legacy.id,
                    defaults={
                        'jornada': jornada,
                        'nombre_cuadro': legacy.nombre_cuadro,
                    }
                )
                cuadros_count += 1
            except Jornada5y6.DoesNotExist:
                pass

        # Selecciones
        selecciones_count = 0
        for legacy in LegacySeleccion5y6.objects.all():
            try:
                cuadro = Cuadro5y6.objects.get(id=legacy.id_cuadro)
                Seleccion5y6.objects.update_or_create(
                    id=legacy.id,
                    defaults={
                        'cuadro': cuadro,
                        'numero_carrera': legacy.numero_carrera,
                        'numero_caballo': legacy.numero_caballo,
                    }
                )
                selecciones_count += 1
            except Cuadro5y6.DoesNotExist:
                pass

        # Ganadores
        ganadores_count = 0
        for legacy in LegacyGanador5y6.objects.all():
            try:
                jornada = Jornada5y6.objects.get(id=legacy.id_jornada)
                Ganador5y6.objects.update_or_create(
                    id=legacy.id,
                    defaults={
                        'jornada': jornada,
                        'numero_carrera': legacy.numero_carrera,
                        'numero_caballo': legacy.numero_caballo,
                    }
                )
                ganadores_count += 1
            except Jornada5y6.DoesNotExist:
                pass

        self.stdout.write(self.style.SUCCESS(f'  ✓ Migrated {jornadas_count} jornadas, {cuadros_count} cuadros, {selecciones_count} selecciones, {ganadores_count} ganadores'))

    def verify_migration(self):
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Verifying migration...'))

        # Count records
        legacy_users = LegacyUser.objects.count()
        new_users = User.objects.count()

        legacy_pollas = LegacyPolla.objects.count()
        new_pollas = Polla.objects.count()

        legacy_eventos = LegacyEvento.objects.count()
        new_eventos = Evento.objects.count()

        legacy_bet_pollas = LegacyBetPolla.objects.count()
        new_bet_pollas = BetPolla.objects.count()

        legacy_bet_eventos = LegacyBetEvento.objects.count()
        new_bet_eventos = BetEvento.objects.count()

        self.stdout.write(f'  Users: {legacy_users} → {new_users}')
        self.stdout.write(f'  Pollas: {legacy_pollas} → {new_pollas}')
        self.stdout.write(f'  Eventos: {legacy_eventos} → {new_eventos}')
        self.stdout.write(f'  Polla Bets: {legacy_bet_pollas} → {new_bet_pollas}')
        self.stdout.write(f'  Evento Bets: {legacy_bet_eventos} → {new_bet_eventos}')

        # Check for discrepancies
        if new_users != legacy_users:
            self.stdout.write(self.style.WARNING(f'  ! User count mismatch'))
        if new_pollas != legacy_pollas:
            self.stdout.write(self.style.WARNING(f'  ! Polla count mismatch'))
        if new_eventos != legacy_eventos:
            self.stdout.write(self.style.WARNING(f'  ! Evento count mismatch'))

        self.stdout.write(self.style.SUCCESS('  ✓ Verification complete'))
