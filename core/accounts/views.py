from django.contrib.auth import views, login
from django.urls import reverse_lazy
from accounts.forms import AuthenticationForm, SignUpForm
from django.views.generic import CreateView
from .models import User


class LoginView(views.LoginView):
    template_name = "accounts/login.html"
    form_class = AuthenticationForm
    redirect_authenticated_user = True
    next_page = "/"


class LogoutView(views.LogoutView):
    template_name = "accounts/logout.html"


class SignUpView(CreateView):
    model = User
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy('website:index')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response