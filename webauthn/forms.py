import base64

from django import forms
from django.contrib.auth import get_user_model

from webauthn.errors import ErrorCodes


class Base64Field(forms.CharField):

    def prepare_value(self, value):
        if value is not None:
            return base64.b64encode(value)

    def to_python(self, value):
        if value is not None:
            return base64.b64decode(value)


class CreateOptionsForm(forms.Form):
    username = forms.CharField()


class GetOptionsForm(forms.Form):
    username = forms.CharField()

    def clean_username(self):
        value = self.cleaned_data['username']
        user_model = get_user_model()
        try:
            user_model.objects.get(username=value)
        except user_model.DoesNotExist:
            raise forms.ValidationError('User does not exist.',
                                        ErrorCodes.UserNotFound.value)
        return value


class RegistrationForm(forms.Form):
    username = Base64Field()
    client_data_json = Base64Field()
    attestation_object = Base64Field()


class VerifyForm(forms.Form):
    username = Base64Field()
    authenticator_data = Base64Field()
    client_data_json = Base64Field()
    signature = Base64Field()
    user_handle = Base64Field()
    raw_id = forms.CharField(required=False)
