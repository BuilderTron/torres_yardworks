"""Integration tests for the three lead-capture views."""

from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from web_app.models import ClientLeads


class LeadViewTestCase(TestCase):
    """Base: clears the process-wide rate-limit cache before each test."""

    def setUp(self):
        cache.clear()


def _quick_data(**overrides):
    data = {
        'name': 'Jane Doe',
        'email': 'jane@example.com',
        'phone': '555-0100',
        'service': 'Lawn & Garden Care',
        'message': 'Please come look at my lawn.',
    }
    data.update(overrides)
    return data


def _contact_data(**overrides):
    data = {
        'name': 'John Smith',
        'email': 'john@example.com',
        'subject': 'Question about pricing',
        'message': 'Hi, what do you charge for cleanup?',
    }
    data.update(overrides)
    return data


def _quote_data(**overrides):
    data = {
        'first_name': 'Sam',
        'last_name': 'Rivera',
        'email': 'sam@example.com',
        'phone': '555-0199',
        'address': '123 Main St, Houston',
        'date': '2026-06-01',
        'service': 'Landscape Design',
        'message': 'Need a quote on landscape design.',
    }
    data.update(overrides)
    return data


class HomeViewTests(LeadViewTestCase):
    def test_get_returns_200(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_valid_post_creates_lead_and_sends_two_emails(self):
        response = self.client.post(reverse('home'), data=_quick_data())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_app/thank_you.html')

        self.assertEqual(ClientLeads.objects.count(), 1)
        lead = ClientLeads.objects.get()
        self.assertEqual(lead.first_name, 'Jane')
        self.assertEqual(lead.last_name, 'Doe')

        self.assertEqual(len(mail.outbox), 2)
        notif, autoreply = mail.outbox
        self.assertIn('[Quick Estimate]', notif.subject)
        self.assertEqual(notif.to, ['info@torresyardworks.com'])
        self.assertEqual(notif.reply_to, ['jane@example.com'])
        self.assertIn('Thanks for contacting', autoreply.subject)
        self.assertEqual(autoreply.to, ['jane@example.com'])
        self.assertEqual(autoreply.reply_to, ['info@torresyardworks.com'])

    def test_invalid_post_renders_index_with_no_email(self):
        response = self.client.post(reverse('home'), data=_quick_data(email='bad'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_app/index.html')
        self.assertEqual(ClientLeads.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_honeypot_rejects_silently_to_user(self):
        response = self.client.post(reverse('home'), data=_quick_data(website='spam'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_app/index.html')
        self.assertEqual(ClientLeads.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)


class ContactViewTests(LeadViewTestCase):
    def test_get_returns_200(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)

    def test_valid_post_creates_lead_and_sends_two_emails(self):
        response = self.client.post(reverse('contact'), data=_contact_data())
        self.assertTemplateUsed(response, 'web_app/thank_you.html')

        self.assertEqual(ClientLeads.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn('[Contact]', mail.outbox[0].subject)

    def test_invalid_post_renders_contact(self):
        response = self.client.post(reverse('contact'), data=_contact_data(email=''))
        self.assertTemplateUsed(response, 'web_app/contact.html')
        self.assertEqual(len(mail.outbox), 0)


class FreeQuoteViewTests(LeadViewTestCase):
    def test_get_returns_200(self):
        response = self.client.get(reverse('free_quote'))
        self.assertEqual(response.status_code, 200)

    def test_valid_post_creates_lead_and_sends_two_emails(self):
        response = self.client.post(reverse('free_quote'), data=_quote_data())
        self.assertTemplateUsed(response, 'web_app/thank_you.html')
        self.assertEqual(ClientLeads.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn('[Free Quote]', mail.outbox[0].subject)

    def test_invalid_post_renders_quote_form(self):
        response = self.client.post(reverse('free_quote'), data=_quote_data(first_name=''))
        self.assertTemplateUsed(response, 'web_app/request_quote.html')
        self.assertEqual(len(mail.outbox), 0)


class RateLimitTests(LeadViewTestCase):
    """Per-IP rate limit on lead POSTs.

    LocMemCache is per-process; tearing down between tests is handled
    by clearing the cache in setUp.
    """

    def setUp(self):
        from django.core.cache import cache
        cache.clear()

    def test_sixth_post_in_a_window_is_blocked(self):
        # First 5 valid POSTs succeed.
        for i in range(5):
            response = self.client.post(reverse('home'), data=_quick_data(email=f'jane{i}@example.com'))
            self.assertEqual(response.status_code, 200, f'POST #{i + 1} failed')

        # 6th is blocked with 429.
        response = self.client.post(reverse('home'), data=_quick_data(email='spam@example.com'))
        self.assertEqual(response.status_code, 429)
        # The 6th submission must NOT have created a lead or sent mail.
        self.assertEqual(ClientLeads.objects.count(), 5)

    def test_rate_limit_does_not_block_get(self):
        # GET is not POST-method-rate-limited; should always serve.
        for _ in range(10):
            response = self.client.get(reverse('home'))
            self.assertEqual(response.status_code, 200)


class EmailFailureProtectsLeadTests(LeadViewTestCase):
    """If Resend (or any send_mail call) explodes, the ClientLead must persist.

    Patches ``send_lead_notification`` to raise; verifies the lead row is
    still created and the request still returns 200.
    """

    def test_notification_send_failure_does_not_lose_lead(self):
        from unittest.mock import patch
        with patch('web_app.views.send_lead_notification', side_effect=RuntimeError('Resend down')):
            response = self.client.post(reverse('home'), data=_quick_data())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ClientLeads.objects.count(), 1)
