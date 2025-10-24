"""
Custom decorators for admin access control

Unlike Django's default @staff_required, we use our own permission system
based on the User.is_admin flag.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """
    Decorator to require admin access (matches PHP's /adm/ area)

    Usage:
        @admin_required
        def manage_pollas(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder al área administrativa')
            return redirect('login')

        if not request.user.is_admin:
            messages.error(request, 'No tienes permisos para acceder al área administrativa')
            return redirect('user_area:dashboard')

        return view_func(request, *args, **kwargs)

    return wrapper


def superadmin_required(view_func):
    """
    Decorator to require superadmin access (for critical operations)

    Usage:
        @superadmin_required
        def delete_user(request, user_id):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión')
            return redirect('login')

        if not request.user.is_superadmin:
            messages.error(request, 'Operación solo permitida para super administradores')
            return redirect('admin_panel:dashboard')

        return view_func(request, *args, **kwargs)

    return wrapper
