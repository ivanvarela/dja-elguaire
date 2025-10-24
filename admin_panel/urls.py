"""
Custom Admin Panel URLs (NOT Django admin)

Matches PHP's /adm/ directory structure
"""
from django.urls import path
from admin_panel import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Polla Management
    path('pollas/', views.manage_pollas, name='manage_pollas'),
    path('pollas/create/', views.create_polla, name='create_polla'),
    path('pollas/<int:polla_id>/delete/', views.delete_polla, name='delete_polla'),
    path('pollas/<int:polla_id>/results/', views.enter_results_polla, name='enter_results_polla'),
    path('pollas/<int:polla_id>/pay/', views.pay_polla, name='pay_polla'),

    # Evento Management
    path('eventos/', views.manage_eventos, name='manage_eventos'),
    path('eventos/create/', views.create_evento, name='create_evento'),
    path('eventos/<int:evento_id>/delete/', views.delete_evento, name='delete_evento'),
    path('eventos/<int:evento_id>/matches/', views.add_matches, name='add_matches'),
    path('eventos/<int:evento_id>/results/', views.enter_results_evento, name='enter_results_evento'),
    path('eventos/<int:evento_id>/pay/', views.pay_evento, name='pay_evento'),

    # User Management (superadmin only)
    path('users/', views.manage_users, name='manage_users'),
]
