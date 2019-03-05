from dataclasses import dataclass

from pywarp import Credential
from pywarp.backends import CredentialStorageBackend


@dataclass
class User:
    email: str
    credential_id: bytes = None
    credential_public_key: bytes = None
    registration_challenge: bytes = None
    authentication_challenge: bytes = None


class SessionBackend(CredentialStorageBackend):
    def __init__(self, request):
        self.session = request.session
        self.key = '__webauthn__%s'

    def get_credential_by_email(self, email):
        user = self.get_user(email)
        return Credential(credential_id=user.credential_id,
                          credential_public_key=user.credential_public_key)

    def save_credential_for_user(self, email, credential):
        self.save(User(
            email=email,
            credential_id=credential.id,
            credential_public_key=bytes(credential.public_key)
        ))

    def save_challenge_for_user(self, email, challenge, type):
        assert type in {"registration", "authentication"}

        user = self.get_user(email)
        setattr(user, type + "_challenge", challenge)
        self.save(user)

    def get_challenge_for_user(self, email, type):
        assert type in {"registration", "authentication"}
        user = self.get_user(email)
        return getattr(user, type + "_challenge")

    def get_user(self, email):
        try:
            user = self.session[self.key % email]
            if user.email == email:
                return user
        except KeyError:
            pass
        return User(email=email)

    def save(self, user: User):
        assert user.email is not None
        self.session[self.key % user.email] = user
