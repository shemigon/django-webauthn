import base64
import json
from dataclasses import dataclass

from botocore import xform_name
from django.http import JsonResponse
from django.utils.functional import cached_property
from django.views import View
from django.views.generic import TemplateView

from pywarp import Credential, RelyingPartyManager
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


class AuthView(TemplateView):
    template_name = 'auth.html'


class BaseView(View):

    @cached_property
    def rp(self):
        request = self.request
        return RelyingPartyManager(
            "PyWARP demo",
            rp_id=request.META['HTTP_HOST'].split(':')[0],
            credential_storage_backend=SessionBackend(request),
            debug=True,
        )


class CredentialCreateOptionsView(BaseView):
    def post(self, request):
        rp = self.rp
        reg_options = rp.get_registration_options(**json.loads(request.body))
        return JsonResponse(reg_options)


class RegisterCredentialView(BaseView):
    def post(self, request):
        rp = self.rp
        req = {xform_name(k): base64.b64decode(v)
               for k, v in json.loads(request.body).items()}
        resp = rp.register(**req)
        return JsonResponse(resp)


class CredentialGetOptionsView(BaseView):
    def post(self, request):
        rp = self.rp
        data = rp.get_authentication_options(**json.loads(request.body))
        return JsonResponse(data)


class VerifyAssertionView(BaseView):
    def post(self, request):
        rp = self.rp
        req = {xform_name(k): base64.b64decode(v)
               for k, v in json.loads(request.body).items()}
        res = rp.verify(**req)
        return JsonResponse(res)
