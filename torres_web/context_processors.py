from django.conf import settings


def show_debug(request):
    return {'show_debug': settings.DEBUG}
