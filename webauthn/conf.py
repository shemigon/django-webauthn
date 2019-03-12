from appconf import AppConf
from django.conf import settings


class WebAuthnConf(AppConf):
    name = 'webauthn'
    verbose_name = 'WebAuthn'

    # need to use settings somehow to enable autoimport without flake8 complain
    NAME = 'WebAuthn App' + (' (debug)' if settings.DEBUG else '')

    HOSTNAME = 'localhost'
    BACKEND = 'webauthn.backends.ModelBackend'

    class Meta:
        prefix = 'webauthn'
