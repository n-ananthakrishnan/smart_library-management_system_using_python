"""App configuration for library app."""
from django.apps import AppConfig


class LibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'library'
    verbose_name = 'Smart Library Management'

    def ready(self):
        # Import signals when app is ready
        import library.signals.handlers
