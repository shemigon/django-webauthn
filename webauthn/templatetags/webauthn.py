from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def webauthn_js(username_input, signup_ctrl, login_ctrl):
    code = '''<script> // django-webauthn initialization script
    window.initWebAuthnHandlers({
      credentialsCreate: "%(create)s",
      credentialsRegister: "%(register)s",
      credentialsGet: "%(get)s",
      verify: "%(verify)s",
      usernameInputSel: "%(user)s",
      signupSel: "%(signup)s",
      loginSel: "%(login)s",
    });
  </script>''' % {
        'create': reverse('webauthn:credentials-create'),
        'register': reverse('webauthn:credentials-register'),
        'get': reverse('webauthn:credentials-get'),
        'verify': reverse('webauthn:verify'),

        'user': username_input,
        'signup': signup_ctrl,
        'login': login_ctrl,
    }
    return mark_safe(code)
