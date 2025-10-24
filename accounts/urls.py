from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('register/', views.registerUser, name='register'),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='accounts/forgot-password.html'),
         name="reset_password"),
    path('reset_password_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/reset_password_sent.html'
    ), name="password_reset_done"),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/reset_password_confirm.html'
    ), name="password_reset_confirm"),
    path('reset_password_complete', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/reset_password_complete.html'
    ), name="password_reset_complete"),
]
