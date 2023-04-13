from django.urls import path
from django.views.generic import RedirectView

from signup.views import EmailLoginView, ProfileView, SignupUserView


urlpatterns = [
    path("", RedirectView.as_view(url="event/list"), name="home"),
    path("accounts/login/", EmailLoginView.as_view(), name="login"),
    path("accounts/profile/", ProfileView.as_view(), name="profile"),
    path("signup/", SignupUserView.as_view(), name="signup"),
]
