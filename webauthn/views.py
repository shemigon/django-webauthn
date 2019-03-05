import base64
import json

from botocore import xform_name
from django.http import JsonResponse
from django.utils.functional import cached_property
from django.views import View

from pywarp import RelyingPartyManager
from .backends import SessionBackend


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
