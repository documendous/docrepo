from django.apps import AppConfig

# from django.core.signals import request_finished


class RepoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "repo"

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from . import signals
