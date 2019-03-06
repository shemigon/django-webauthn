import base64

from django import forms


class Base64Field(forms.CharField):

    def prepare_value(self, value):
        if value is not None:
            return base64.b64encode(value)

    def to_python(self, value):
        if value is not None:
            return base64.b64decode(value)


class CreateOptionsForm(forms.Form):
    username = forms.CharField()


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
