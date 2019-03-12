import base64

from django import forms


class Base64Field(forms.CharField):

    def prepare_value(self, value):
        if value is not None:
            return base64.b64encode(value)

    def to_python(self, value):
        if value is not None:
            return base64.b64decode(value)
