from django.db import models

from .conf import settings


class WebAuthnUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, models.CASCADE,
                                related_name='webauthn')
    credential_id = models.BinaryField(blank=True, null=True)
    credential_public_key = models.BinaryField(blank=True, null=True)
    registration_challenge = models.BinaryField(blank=True, null=True)
    authentication_challenge = models.BinaryField(blank=True, null=True)

    def __str__(self):
        return str(self.user_id)
