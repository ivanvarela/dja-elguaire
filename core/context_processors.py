"""
Context Processors - Make variables available in all templates
"""
from django.conf import settings


def site_context(request):
    """Add site-wide context variables to all templates"""
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_URL': settings.SITE_URL,
        'user_balance': request.user.get_balance() if request.user.is_authenticated else 0,
    }
