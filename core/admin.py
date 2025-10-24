"""
Django Admin Configuration (Optional - We use custom admin panel)

This is the built-in Django admin. We're creating a custom admin interface,
but this can be useful for debugging and database inspection.
"""
from django.contrib import admin
from core.models import (
    User, Racetrack, League, Team, Polla, Evento, Match,
    BetPolla, BetEvento, BetMatch, AccountTransaction, EventTransaction
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'alias', 'is_admin', 'is_active', 'date_joined')
    list_filter = ('is_admin', 'is_active')
    search_fields = ('email', 'alias')


@admin.register(Racetrack)
class RacetrackAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pais')
    search_fields = ('nombre',)


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'pais')
    search_fields = ('name',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'league', 'pais')
    list_filter = ('league',)
    search_fields = ('nombre',)


@admin.register(Polla)
class PollaAdmin(admin.ModelAdmin):
    list_display = ('code4', 'racetrack', 'date_race', 'status', 'price_entry')
    list_filter = ('status', 'racetrack')
    search_fields = ('code4',)


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('code4', 'name', 'league', 'date', 'status', 'price_entry')
    list_filter = ('status', 'league')
    search_fields = ('code4', 'name')


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('evento', 'team1', 'team2', 'date', 'score_team1', 'score_team2')
    list_filter = ('evento',)


@admin.register(BetPolla)
class BetPollaAdmin(admin.ModelAdmin):
    list_display = ('user', 'polla', 'pto_tot', 'date_bet')
    list_filter = ('polla',)
    search_fields = ('user__email', 'user__alias')


@admin.register(BetEvento)
class BetEventoAdmin(admin.ModelAdmin):
    list_display = ('user', 'evento', 'puntos', 'date_bet')
    list_filter = ('evento',)
    search_fields = ('user__email', 'user__alias')


@admin.register(AccountTransaction)
class AccountTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'qty', 'trx_date', 'conciliado')
    list_filter = ('tipo', 'conciliado')
    search_fields = ('user__email', 'comment')


@admin.register(EventTransaction)
class EventTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'qty', 'trx_date', 'conciliado')
    list_filter = ('tipo', 'conciliado')
    search_fields = ('user__email', 'comment')
