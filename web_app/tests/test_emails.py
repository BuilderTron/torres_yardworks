"""Tests for the lead-email helpers in ``web_app/emails.py``.

Uses Django's locmem email backend (the default under ``TestCase``) so
sends end up in ``django.core.mail.outbox`` instead of going to Resend.
"""

from django.core import mail
from django.test import TestCase

from web_app.emails import send_lead_autoreply, send_lead_notification
from web_app.models import ClientLeads


def _make_lead(**overrides) -> ClientLeads:
    defaults = dict(
        first_name='Jane',
        last_name='Doe',
        email='jane@example.com',
        phone='555-0100',
        address='',
        date='',
        service='Lawn & Garden Care',
        subject='',
        message='Hi, please call me about my front yard.',
    )
    defaults.update(overrides)
    return ClientLeads.objects.create(**defaults)


class SendLeadNotificationTests(TestCase):
    def test_sends_owner_notification_with_customer_reply_to(self):
        lead = _make_lead()
        send_lead_notification(lead, form_name='Contact')

        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.to, ['info@torresyardworks.com'])
        self.assertEqual(msg.reply_to, ['jane@example.com'])
        self.assertEqual(msg.from_email, 'Torres Yardworks <info@torresyardworks.com>')
        self.assertIn('[Contact]', msg.subject)
        self.assertIn('Jane Doe', msg.subject)
        self.assertIn('Hi, please call me', msg.body)

    def test_includes_html_alternative(self):
        send_lead_notification(_make_lead(), form_name='Contact')
        msg = mail.outbox[0]
        html_parts = [a for a in msg.alternatives if a[1] == 'text/html']
        self.assertEqual(len(html_parts), 1)
        self.assertIn('Jane Doe', html_parts[0][0])

    def test_missing_email_skips_reply_to(self):
        # An incomplete lead (no email) shouldn't crash — Reply-To just drops.
        lead = _make_lead(email='')
        send_lead_notification(lead, form_name='Quick Estimate')
        self.assertEqual(mail.outbox[0].reply_to, [])


class SendLeadAutoreplyTests(TestCase):
    def test_sends_to_customer_with_team_reply_to(self):
        lead = _make_lead()
        send_lead_autoreply(lead, form_name='Quick Estimate')

        msg = mail.outbox[0]
        self.assertEqual(msg.to, ['jane@example.com'])
        self.assertEqual(msg.reply_to, ['info@torresyardworks.com'])
        self.assertEqual(msg.from_email, 'Torres Yardworks <info@torresyardworks.com>')
        self.assertIn('Thanks for contacting', msg.subject)
        self.assertIn('Jane', msg.body)
        # Form-name is lowercased into the body sentence
        self.assertIn('quick estimate', msg.body.lower())

    def test_includes_html_alternative(self):
        send_lead_autoreply(_make_lead(), form_name='Free Quote')
        msg = mail.outbox[0]
        self.assertEqual(len(msg.alternatives), 1)
        self.assertEqual(msg.alternatives[0][1], 'text/html')
