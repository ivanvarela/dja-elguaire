"""
Core Views - Public area (login, register, password recovery)
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.forms import LoginForm, RegisterForm, PasswordRecoveryForm


def home(request):
    """Home page - shows login form"""
    if request.user.is_authenticated:
        return redirect('user_area:dashboard')

    return render(request, 'core/home.html', {
        'title': 'La Polla - ElGuaire'
    })


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('user_area:dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido {user.alias}!')
                return redirect('user_area:dashboard')
            else:
                messages.error(request, 'Email o contraseña incorrectos')
    else:
        form = LoginForm()

    return render(request, 'core/login.html', {
        'form': form,
        'title': 'Ingresar'
    })


def register_view(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('user_area:dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Cuenta creada exitosamente. Por favor inicia sesión.')
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'core/register.html', {
        'form': form,
        'title': 'Registrarse'
    })


@login_required
def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('home')


def password_recovery(request):
    """Password recovery"""
    if request.method == 'POST':
        form = PasswordRecoveryForm(request.POST)
        if form.is_valid():
            # TODO: Implement password recovery email
            messages.success(request, 'Se ha enviado un email con instrucciones para recuperar tu contraseña')
            return redirect('login')
    else:
        form = PasswordRecoveryForm()

    return render(request, 'core/password_recovery.html', {
        'form': form,
        'title': 'Recuperar Contraseña'
    })
