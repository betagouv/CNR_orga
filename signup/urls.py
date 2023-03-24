from django.urls import path

from signup.views import EmailLoginView, ProfilView, SignupUserView


urlpatterns = [
    path("accounts/login/", EmailLoginView.as_view(), name="login"),
    path("accounts/profil/", ProfilView.as_view(), name="profil"),
    path("signup/", SignupUserView.as_view(), name="signup"),
]
