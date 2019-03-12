import json

from django.contrib.auth import login
from django.db import IntegrityError
from django.http import JsonResponse
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.views import View

from pywarp import RelyingPartyManager
from .conf import settings
from .forms import CreateOptionsForm, GetOptionsForm, RegistrationForm, \
    VerifyForm


class BaseView(View):
    @cached_property
    def rp(self):
        backend = import_string(settings.WEBAUTHN_BACKEND)()

        return RelyingPartyManager(
            settings.WEBAUTHN_NAME,
            rp_id=settings.WEBAUTHN_HOSTNAME,
            credential_storage_backend=backend,
            debug=True,
        )


# signup views

class CredentialCreateOptionsView(BaseView):
    def post(self, request):
        form = CreateOptionsForm(json.loads(request.body))
        if not form.is_valid():
            return JsonResponse({
                'errors': form.errors.as_json(),
            })
        rp = self.rp
        data = form.cleaned_data
        try:
            reg_options = rp.get_registration_options(
                username=data['username'],
                full_name=data.get('full_name', None),
            )
        except IntegrityError:
            return JsonResponse({
                'errors': 'User "%s" already exists.' % data['username']
            })
        return JsonResponse(reg_options)


class RegisterCredentialView(BaseView):
    def post(self, request):
        form = RegistrationForm(json.loads(request.body))
        if not form.is_valid():
            return JsonResponse({
                'errors': form.errors.as_json()
            })
        rp = self.rp
        data = form.cleaned_data
        resp = rp.register(
            client_data_json=data.pop('client_data_json'),
            attestation_object=data.pop('attestation_object'),
            username=data.pop('username'),
            **data
        )
        return JsonResponse(resp)


# login views

class CredentialGetOptionsView(BaseView):
    def post(self, request):
        form = GetOptionsForm(json.loads(request.body))
        if not form.is_valid():
            return JsonResponse({
                'errors': form.errors.as_json()
            })
        rp = self.rp
        data = rp.get_authentication_options(
            username=form.cleaned_data['username'],
        )
        return JsonResponse(data)


class VerifyAssertionView(BaseView):
    def post(self, request):
        form = VerifyForm(json.loads(request.body))
        if not form.is_valid():
            return JsonResponse({
                'errors': form.errors.as_json()
            })
        verified = self.rp.verify(**form.cleaned_data)
        if verified:
            user = form.get_user()
            login(request, user)
        return JsonResponse({"verified": verified})
