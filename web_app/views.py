import logging

from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .emails import send_lead_autoreply, send_lead_notification
from .forms import ContactForm, FreeQuoteForm, HomeQuickForm
from .models import Event, GalleryUpload, HeroSlide, Testimonies

logger = logging.getLogger(__name__)


def _client_ip(request) -> str:
    """Extract the originating client IP, honoring X-Forwarded-For from Caddy."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _handle_lead_post(request, form, *, form_name: str):
    """Save the lead, fire both emails, return the rendered thank-you page.

    Email failures are logged but do NOT roll back the lead — the row in
    ``ClientLeads`` is the source of truth; the email is a convenience
    notification. The owner can always recover the lead via the admin
    export (`django-import-export`).
    """
    lead = form.save()
    try:
        send_lead_notification(lead, form_name=form_name)
    except Exception:  # noqa: BLE001 — we deliberately swallow to protect lead persistence
        logger.exception("Failed to send lead notification for ClientLeads #%s", lead.pk)
    try:
        send_lead_autoreply(lead, form_name=form_name)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to send autoreply for ClientLeads #%s", lead.pk)
    return render(request, 'web_app/thank_you.html', {'first_name': lead.first_name})


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------


def health_check(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return JsonResponse({"status": "ok"})


@require_http_methods(["GET", "POST"])
def home(request):
    if request.method == "POST":
        form = HomeQuickForm(data=request.POST, remote_ip=_client_ip(request))
        if form.is_valid():
            return _handle_lead_post(request, form, form_name='Quick Estimate')
    else:
        form = HomeQuickForm(remote_ip=_client_ip(request))

    return render(request, 'web_app/index.html', {
        'slides': HeroSlide.objects.all(),
        'events': Event.objects.all(),
        'testimonys': Testimonies.objects.all(),
        'form': form,
    })


def about(request):
    return render(request, 'web_app/about.html', {})


def services(request):
    return render(request, 'web_app/services.html', {})


def lawn(request):
    return render(request, 'web_app/lawn_gardencare.html', {})


def landscape(request):
    return render(request, 'web_app/landscape_design.html', {})


def outdoor(request):
    return render(request, 'web_app/outdoor_remodel.html', {})


def indoor(request):
    return render(request, 'web_app/indoor_remodel.html', {})


def gallery(request):
    return render(request, 'web_app/gallery.html', {'photos': GalleryUpload.objects.all()})


@require_http_methods(["GET", "POST"])
def contact(request):
    if request.method == "POST":
        form = ContactForm(data=request.POST, remote_ip=_client_ip(request))
        if form.is_valid():
            return _handle_lead_post(request, form, form_name='Contact')
    else:
        form = ContactForm(remote_ip=_client_ip(request))

    return render(request, 'web_app/contact.html', {'form': form})


@require_http_methods(["GET", "POST"])
def free_quote(request):
    if request.method == "POST":
        form = FreeQuoteForm(data=request.POST, remote_ip=_client_ip(request))
        if form.is_valid():
            return _handle_lead_post(request, form, form_name='Free Quote')
    else:
        form = FreeQuoteForm(remote_ip=_client_ip(request))

    return render(request, 'web_app/request_quote.html', {'form': form})


def thank_you(request):
    return render(request, 'web_app/thank_you.html', {})


# Test page for models and forms
def test(request):
    return render(request, 'web_app/test.html')
