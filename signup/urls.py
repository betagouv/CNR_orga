from django.urls import path

from signup.views import EmailLoginView, ProfileView, SignupUserView


urlpatterns = [
    path("accounts/login/", EmailLoginView.as_view(), name="login"),
    path("accounts/profile/", ProfileView.as_view(), name="profile"),
    path("signup/", SignupUserView.as_view(), name="signup"),
]
