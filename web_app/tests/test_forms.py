"""Tests for the lead-capture forms."""

from django.test import TestCase

from web_app.forms import ContactForm, FreeQuoteForm, HomeQuickForm
from web_app.models import ClientLeads


def _valid_quick_form_data(**overrides):
    data = {
        'name': 'Jane Doe',
        'email': 'jane@example.com',
        'phone': '555-0100',
        'service': 'Lawn & Garden Care',
        'message': 'Please come look at my lawn.',
    }
    data.update(overrides)
    return data


def _valid_contact_form_data(**overrides):
    data = {
        'name': 'John Smith',
        'email': 'john@example.com',
        'subject': 'Question about pricing',
        'message': 'Hi, what do you charge for cleanup?',
    }
    data.update(overrides)
    return data


def _valid_quote_form_data(**overrides):
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


class HomeQuickFormTests(TestCase):
    def test_valid_submission_creates_lead_with_split_name(self):
        form = HomeQuickForm(data=_valid_quick_form_data())
        self.assertTrue(form.is_valid(), form.errors)
        lead = form.save()
        self.assertEqual(lead.first_name, 'Jane')
        self.assertEqual(lead.last_name, 'Doe')
        self.assertEqual(lead.email, 'jane@example.com')
        self.assertEqual(lead.service, 'Lawn & Garden Care')

    def test_single_word_name_becomes_first_with_empty_last(self):
        form = HomeQuickForm(data=_valid_quick_form_data(name='Cher'))
        self.assertTrue(form.is_valid(), form.errors)
        lead = form.save()
        self.assertEqual(lead.first_name, 'Cher')
        self.assertEqual(lead.last_name, '')

    def test_three_word_name_splits_at_first_space(self):
        form = HomeQuickForm(data=_valid_quick_form_data(name='Jane Q Doe'))
        self.assertTrue(form.is_valid())
        lead = form.save()
        self.assertEqual(lead.first_name, 'Jane')
        self.assertEqual(lead.last_name, 'Q Doe')

    def test_honeypot_rejects(self):
        form = HomeQuickForm(data=_valid_quick_form_data(website='http://spam.example'))
        self.assertFalse(form.is_valid())
        self.assertIn('website', form.errors)
        self.assertEqual(ClientLeads.objects.count(), 0)

    def test_missing_required_field(self):
        form = HomeQuickForm(data=_valid_quick_form_data(email=''))
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_invalid_email_format(self):
        form = HomeQuickForm(data=_valid_quick_form_data(email='not-an-email'))
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class ContactFormTests(TestCase):
    def test_valid_submission(self):
        form = ContactForm(data=_valid_contact_form_data())
        self.assertTrue(form.is_valid(), form.errors)
        lead = form.save()
        self.assertEqual(lead.first_name, 'John')
        self.assertEqual(lead.last_name, 'Smith')
        self.assertEqual(lead.subject, 'Question about pricing')

    def test_honeypot_rejects(self):
        form = ContactForm(data=_valid_contact_form_data(website='x'))
        self.assertFalse(form.is_valid())


class FreeQuoteFormTests(TestCase):
    def test_valid_submission(self):
        form = FreeQuoteForm(data=_valid_quote_form_data())
        self.assertTrue(form.is_valid(), form.errors)
        lead = form.save()
        self.assertEqual(lead.first_name, 'Sam')
        self.assertEqual(lead.last_name, 'Rivera')
        self.assertEqual(lead.address, '123 Main St, Houston')

    def test_missing_first_name(self):
        form = FreeQuoteForm(data=_valid_quote_form_data(first_name=''))
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_honeypot_rejects(self):
        form = FreeQuoteForm(data=_valid_quote_form_data(website='x'))
        self.assertFalse(form.is_valid())
