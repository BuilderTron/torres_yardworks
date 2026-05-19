"""Lead-capture forms.

Three public forms, all ``ModelForm`` subclasses backed by ``ClientLeads``.
Common machinery (honeypot, Cloudflare Turnstile, name-splitting) lives on
``LeadFormBase``; the subclasses only declare which model fields each page
collects.

Honeypot: a hidden ``website`` field. Bots fill every input they see; real
users never touch a CSS-hidden one. Non-empty value → form invalid.

Turnstile: ``django-turnstile``'s ``TurnstileField`` performs the
server-side siteverify call against Cloudflare. In tests the network call
is disabled by setting ``TURNSTILE_ENABLE = False`` (see tests/__init__.py).
"""

from __future__ import annotations

from django import forms

from turnstile.fields import TurnstileField

from web_app.models import ClientLeads


class HoneypotMixin:
    """Adds a hidden ``website`` field. Bots fill it; humans don't."""

    def clean_website(self):
        if self.cleaned_data.get('website'):
            # Generic message — don't tip off the bot which field tripped it.
            raise forms.ValidationError('Submission rejected.')
        return ''


class LeadFormBase(HoneypotMixin, forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={
            'autocomplete': 'off',
            'tabindex': '-1',
            # CSS-hidden via inline style as a belt-and-braces fallback if
            # the global stylesheet doesn't already hide HiddenInput.
            'style': 'position:absolute;left:-9999px;',
            'aria-hidden': 'true',
        }),
        label='',
    )
    captcha = TurnstileField()

    class Meta:
        model = ClientLeads
        fields: list[str] = []  # subclasses must override

    def __init__(self, *args, remote_ip: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        # Pass the client IP to TurnstileField so siteverify includes it.
        self.fields['captcha'].remote_ip = remote_ip


# ---------------------------------------------------------------------------
# Forms that collect a single "Name" field (Home quick form, Contact page)
# ---------------------------------------------------------------------------


class _SingleNameLeadForm(LeadFormBase):
    """Helper base for forms that collect one ``name`` input.

    On save the name is split on the first space — 'Jane Doe' becomes
    first='Jane', last='Doe', while 'Cher' becomes first='Cher', last=''.
    """

    name = forms.CharField(max_length=200, label='Name')

    class Meta(LeadFormBase.Meta):
        fields: list[str] = []  # subclasses set this

    def save(self, commit: bool = True):
        instance: ClientLeads = super().save(commit=False)
        name = (self.cleaned_data.get('name') or '').strip()
        if ' ' in name:
            first, last = name.split(' ', 1)
        else:
            first, last = name, ''
        instance.first_name = first
        instance.last_name = last
        if commit:
            instance.save()
        return instance


class HomeQuickForm(_SingleNameLeadForm):
    class Meta(_SingleNameLeadForm.Meta):
        fields = ['email', 'phone', 'service', 'message']


class ContactForm(_SingleNameLeadForm):
    class Meta(_SingleNameLeadForm.Meta):
        fields = ['email', 'subject', 'message']


# ---------------------------------------------------------------------------
# Free quote — full split first/last + address + date
# ---------------------------------------------------------------------------


class FreeQuoteForm(LeadFormBase):
    class Meta(LeadFormBase.Meta):
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'date', 'service', 'message',
        ]
