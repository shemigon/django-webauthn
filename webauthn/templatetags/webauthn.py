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
