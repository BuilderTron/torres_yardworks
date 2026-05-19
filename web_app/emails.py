"""Email helpers for the lead-form pipeline.

Two messages go out per submission:

* ``send_lead_notification`` — owner-facing alert delivered to ``LEADS_EMAIL``.
  ``Reply-To`` is the customer so hitting reply in the inbox goes straight
  back to the customer.

* ``send_lead_autoreply`` — customer-facing acknowledgement. ``Reply-To`` is
  ``LEADS_EMAIL`` so the customer's reply lands in the team inbox.

Both messages route through ``EMAIL_BACKEND`` (Resend in prod via
``django-anymail``, console backend in dev). Templates live under
``web_app/templates/web_app/emails/`` with ``.txt`` + ``.html`` companions.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@dataclass(frozen=True)
class LeadContext:
    """Subset of fields rendered into both email templates.

    Built from a ``ClientLeads`` instance plus the form name. Keeping this
    a plain dataclass (not the model) keeps the templates decoupled from
    model internals and makes unit-testing trivial.
    """

    form_name: str  # 'Quick Estimate', 'Contact', or 'Free Quote'
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    date: str
    service: str
    subject: str
    message: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


def context_from_lead(lead, form_name: str) -> LeadContext:
    """Build a ``LeadContext`` from a saved ``ClientLeads`` instance."""
    return LeadContext(
        form_name=form_name,
        first_name=lead.first_name or '',
        last_name=lead.last_name or '',
        email=lead.email or '',
        phone=lead.phone or '',
        address=lead.address or '',
        date=lead.date or '',
        service=lead.service or '',
        subject=lead.subject or '',
        message=lead.message or '',
    )


def _send(
    *,
    subject: str,
    template_base: str,
    to: list[str],
    reply_to: list[str],
    context: LeadContext,
) -> None:
    body_txt = render_to_string(f'web_app/emails/{template_base}.txt', {'lead': context})
    body_html = render_to_string(f'web_app/emails/{template_base}.html', {'lead': context})
    msg = EmailMultiAlternatives(
        subject=subject,
        body=body_txt,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to,
        reply_to=reply_to,
    )
    msg.attach_alternative(body_html, 'text/html')
    msg.send(fail_silently=False)


def send_lead_notification(lead, form_name: str) -> None:
    """Notify the team about a new lead. Owner-facing."""
    ctx = context_from_lead(lead, form_name)
    subject = f"[{form_name}] New lead from {ctx.full_name or ctx.email}"
    _send(
        subject=subject,
        template_base='lead_notification',
        to=[settings.LEADS_EMAIL],
        reply_to=[ctx.email] if ctx.email else [],
        context=ctx,
    )


def send_lead_autoreply(lead, form_name: str) -> None:
    """Acknowledge to the customer that we received their message."""
    ctx = context_from_lead(lead, form_name)
    subject = "Thanks for contacting Torres Yardworks"
    _send(
        subject=subject,
        template_base='lead_autoreply',
        to=[ctx.email],
        reply_to=[settings.LEADS_EMAIL],
        context=ctx,
    )
