"""Test package.

Disable the django-turnstile network call for the entire test run. The
module-level ``ENABLE`` flag is captured at import time so ``override_settings``
in individual tests doesn't reach it — patching here ensures every TestCase
sees a quiet, offline TurnstileField.
"""

import turnstile.fields as _turnstile_fields
import turnstile.widgets as _turnstile_widgets

_turnstile_fields.ENABLE = False
_turnstile_widgets.ENABLE = False
