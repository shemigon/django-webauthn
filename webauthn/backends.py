from django.contrib.auth import get_user_model

from pywarp import Credential
from pywarp.backends import AbstractStorageBackend
from webauthn.models import WebAuthnUser


class ModelBackend(AbstractStorageBackend):
    def __init__(self):
        self.user_model = get_user_model()

    def get_credential(self, username):
        user = self.user_model.objects.get_by_natural_key(username).webauthn
        return Credential(credential_id=user.credential_id,
                          credential_public_key=user.credential_public_key)

    def save_credential(self, username, credential, **user_extra):
        user = self.user_model.objects.get_by_natural_key(username).webauthn
        user.credential_id = credential.id
        user.credential_public_key = bytes(credential.public_key)
        user.save()

    def save_challenge(self, username, challenge, challenge_type):
        assert challenge_type in {"registration", "authentication"}

        if challenge_type == 'registration':
            WebAuthnUser.objects.create(
                user=self.user_model.objects.create(**{
                    self.user_model.USERNAME_FIELD: username
                }),
                registration_challenge=challenge,
            )
        else:
            user = self.user_model.objects.get_by_natural_key(username).webauthn
            user.authentication_challenge = challenge
            user.save()

    def get_challenge(self, username, challenge_type):
        assert challenge_type in {"registration", "authentication"}

        user = self.user_model.objects.get_by_natural_key(username).webauthn
        return getattr(user, challenge_type + "_challenge")
