"""
User Area URLs - Authenticated user interface

Matches PHP's /inside/ directory
"""
from django.urls import path
from user_area import views

app_name = 'user_area'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Betting
    path('polla/<int:polla_id>/bet/', views.place_bet_polla, name='place_bet_polla'),
    path('evento/<int:evento_id>/bet/', views.place_bet_evento, name='place_bet_evento'),

    # Account
    path('account/', views.account_detail, name='account_detail'),
    path('my-bets/', views.my_bets, name='my_bets'),

    # Results
    path('results/polla/<int:polla_id>/', views.view_results, name='view_results_polla'),
    path('results/evento/<int:evento_id>/', views.view_results, name='view_results_evento'),
]
