"""
Root conftest.py for pytest.

Sets the Django settings module so tests can run without env vars.
"""

import django
from django.conf import settings


def pytest_configure(config):
    """Configure Django settings for the test suite."""
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gmao.settings.dev")
