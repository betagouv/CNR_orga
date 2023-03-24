from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from signup.forms import LoginForm, SignupUserForm


class EmailLoginView(LoginView):
    template_name = "registration/login.html"
    form_class = LoginForm


class SignupUserView(CreateView):
    template_name = "signup/signup.html"
    form_class = SignupUserForm
    success_url = reverse_lazy("login")


class ProfilView(LoginRequiredMixin, TemplateView):
    template_name = "signup/profil.html"
