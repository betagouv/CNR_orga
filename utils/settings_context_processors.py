from django.conf import settings


def expose_settings(request):
    """
    Put things into the context to make them available in templates.
    https://docs.djangoproject.com/en/4.1/ref/templates/api/#using-requestcontext
    """
    base_template = "base_htmx.html" if getattr(request, "htmx", False) else "base.html"

    return {
        "BASE_TEMPLATE": base_template,
        "ALLOWED_HOSTS": settings.ALLOWED_HOSTS,
    }
