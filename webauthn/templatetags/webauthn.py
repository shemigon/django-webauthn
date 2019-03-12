from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def webauthn_login_js(username_input, control_selector=''):
    code = '''<script>
    (function () {
      Object.assign(window.webauthn.params, {
        urlCredentialsGet: "%(get)s",
        urlVerify: "%(verify)s"
      });
      window.webauthn.addLoginHandler({
        usernameInputSel: "%(user)s",
        buttonSel: "%(login)s",
      });
    }());
  </script>''' % {
        'get': reverse('webauthn:credentials-get'),
        'verify': reverse('webauthn:verify'),
        'user': username_input,
        'login': control_selector,
    }
    return mark_safe(code)


@register.simple_tag
def webauthn_signup_js(username_input, control_selector=''):
    code = '''<script> // django-webauthn initialization script
    Object.assign(window.webauthn.params, {
      urlCredentialsCreate: "%(create)s",
      urlCredentialsRegister: "%(register)s",
    });
    window.webauthn.addSignupHandler({
      usernameInputSel: "%(user)s",
      buttonSel: "%(control)s",
    });
  </script>''' % {
        'create': reverse('webauthn:credentials-create'),
        'register': reverse('webauthn:credentials-register'),
        'user': username_input,
        'control': control_selector,
    }
    return mark_safe(code)
