import uuid

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from signup.models import OrganizerEmail


class SignupUserForm(UserCreationForm):
    first_name = forms.CharField(
        label="Prénom",
        required=True,
        widget=forms.TextInput(attrs={"class": "fr-input"}),
    )
    last_name = forms.CharField(
        label="Nom", required=True, widget=forms.TextInput(attrs={"class": "fr-input"})
    )
    email = forms.EmailField(
        required=True, widget=forms.TextInput(attrs={"class": "fr-input"})
    )

    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(SignupUserForm, self).save(commit=False)
        user.username = uuid.uuid4().hex
        user.is_organizer = OrganizerEmail.objects.filter(email=user.email).exists()

        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        required=True, widget=forms.TextInput(attrs={"class": "fr-input"})
    )
