from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'


class LoggedInView(LoginRequiredMixin, TemplateView):
    template_name = 'logged-in.html'


class SignedUpView(TemplateView):
    template_name = 'signed-up.html'
