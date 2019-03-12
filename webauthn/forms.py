from django import forms
from django.contrib.auth import get_user_model

from .errors import ErrorCodes
from .fields import Base64Field


class CreateOptionsForm(forms.Form):
    username = forms.CharField()

    def clean_username(self):
        value = self.cleaned_data['username']
        user_model = get_user_model()
        try:
            user_model.objects.get_by_natural_key(value)
            raise forms.ValidationError('User already exist.',
                                        ErrorCodes.UserAlreadyExists.value)
        except user_model.DoesNotExist:
            pass
        return value


class GetOptionsForm(forms.Form):
    username = forms.CharField()

    def clean_username(self):
        value = self.cleaned_data['username']
        user_model = get_user_model()
        try:
            user_model.objects.get_by_natural_key(value)
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

    def get_user(self):
        if self.is_valid():
            user = get_user_model().objects.get_by_natural_key(
                self.cleaned_data['username'].decode()
            )
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            return user
