import os

# Default to dev settings if DJANGO_SETTINGS_MODULE is not set
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gmao.settings.dev')
