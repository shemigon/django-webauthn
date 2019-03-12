from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import SignupForm


class SignupRequiredMixin(LoginRequiredMixin):
    pass


class HomeView(TemplateView):
    template_name = 'home.html'


class LoggedInView(LoginRequiredMixin, TemplateView):
    template_name = 'logged-in.html'


class SignedUpView(SignupRequiredMixin, FormView):
    template_name = 'signed-up.html'
    form_class = SignupForm
    success_url = reverse_lazy('signup-complete')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs


class SignupCompleteView(TemplateView):
    template_name = 'signup-complete.html'
