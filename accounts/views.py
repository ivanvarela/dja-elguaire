import pdb

from django.shortcuts import render, redirect
from dashb.models import Profile
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from django.db import transaction
from django.core.mail import EmailMessage


# Create your views here.


def loginPage(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except Exception as e:
            messages.error(request, 'Usuario no encontrado, debe registrarse')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                profile = Profile.objects.get(id=user.profile.id)
                if profile.is_admin or profile.status == 'A':
                    return redirect('dashb:home')
                else:
                    messages.error(request, 'Usuario no activo, hable con el administrador')
            except Exception as e:
                return redirect('login')
        else:
            messages.error(request, 'Usuario o password incorrrecto')

    return render(request, 'accounts/sign-in.html')


def logoutPage(request):
    logout(request)
    messages.success(request, "Sesión cerrada")
    return redirect('login')


def registerUser(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                first_name = form.cleaned_data['first_name'].title()
                last_name = form.cleaned_data['last_name'].title()

                user = form.save(commit=False)
                user.first_name = first_name
                user.last_name = last_name
                user.email = user.username
                user.save()

                profile = Profile.objects.create(
                    user=user,
                    activo=True,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['username'],
                )

            # Creo el profile con status ='P'
            messages.success(request, 'Usuario Registrado, debe esperar su activación')

            subject = f'NUEVO REGISTRO - {user.first_name} {user.last_name}'
            link = """<a href='https://dash.mediosmasivos.com.mx/dash/profiles/'>Ingresa aquí para aprobar el registro</a>"""
            message = f"Recuerda activar y colocar la unidad correspondiente {link}  para activarlo a: {user.email}"
            from_email = 'info@mediosmasivos.com.mx'
            recipient_list = [
                'alan.delgado@mediosmasivos.com.mx',
                'jesus.mendez@mediosmasivos.com.mx',
                'ivan.varela@mediosmasivos.com.mx',
            ]

            email = EmailMessage(
                subject=subject,
                from_email=from_email,
                body=message,
                to=recipient_list)

            email.content_subtype = "html"

            email.send()

            return redirect('login')
        else:
            messages.error(request, 'Ha ocurrido un error usuario no creado')
            for e in form.errors:
                messages.error(request, e)
                return render(request, 'accounts/sign-up.html', {'form': form})
    else:
        form = CustomUserCreationForm()

    context = {'form': form}
    return render(request, 'accounts/sign-up.html', context=context)
