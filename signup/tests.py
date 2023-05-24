from django.test import TestCase
from django.urls import reverse

from signup.factories import DEFAULT_PASSWORD, EmailBasedUserFactory, OrganizerEmailFactory
from signup.models import EmailBasedUser


class LoginTest(TestCase):
    def setUp(self):
        self.url = reverse("login")
        self.user = EmailBasedUserFactory()

    def test_login_form_with_correct_password(self):
        response = self.client.post(self.url, {"username": self.user.email, "password": DEFAULT_PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))

    def test_login_form_with_wrong_password(self):
        response = self.client.post(self.url, {"username": self.user.email, "password": "wrongpassword"})
        self.assertContains(response, "Saisissez une adresse email et un mot de passe valides.")


class SignupTest(TestCase):
    def setUp(self):
        self.url = reverse("signup")

        # generate 3 fake users
        for _ in range(3):
            EmailBasedUserFactory()

    def test_redirection_to_login_page(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login") + "?next=" + reverse("profile"))

        response_login = self.client.get(response.url)
        self.assertEqual(response_login.status_code, 200)

    def test_signup_with_already_exist_email(self):
        existing_user = EmailBasedUser.objects.first()
        new_user = EmailBasedUserFactory.stub(email=existing_user.email)
        form_data = {
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email": new_user.email,
            "password1": DEFAULT_PASSWORD,
            "password2": DEFAULT_PASSWORD,
        }

        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cette adresse email est déjà utilisée")

    def test_signup_without_cgu_checked(self):
        new_user = EmailBasedUserFactory.stub()
        form_data = {
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email": new_user.email,
            "password1": DEFAULT_PASSWORD,
            "password2": DEFAULT_PASSWORD,
        }

        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ce champ est obligatoire.")

    def test_signup_with_unknown_email(self):
        self.assertEqual(EmailBasedUser.objects.count(), 3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        new_user = EmailBasedUserFactory.stub()
        form_data = {
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email": new_user.email,
            "password1": DEFAULT_PASSWORD,
            "password2": DEFAULT_PASSWORD,
            "cgu": True,
        }
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

        self.assertEqual(EmailBasedUser.objects.count(), 4)
        first_user = EmailBasedUser.objects.first()
        self.assertEqual(first_user.is_organizer, False)

        response = self.client.post(reverse("login"), {"username": new_user.email, "password": DEFAULT_PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))

    def test_signup_with_organizer_email(self):
        self.assertEqual(EmailBasedUser.objects.count(), 3)

        organizer = OrganizerEmailFactory()
        new_user = EmailBasedUserFactory.stub(email=organizer.email)
        form_data = {
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email": new_user.email,
            "password1": DEFAULT_PASSWORD,
            "password2": DEFAULT_PASSWORD,
            "cgu": True,
        }

        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

        self.assertEqual(EmailBasedUser.objects.count(), 4)

        saved_user = EmailBasedUser.objects.filter(email=new_user.email).first()
        self.assertEqual(saved_user.is_organizer, True)

        response = self.client.post(reverse("login"), {"username": new_user.email, "password": DEFAULT_PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("profile"), status_code=302, target_status_code=302, fetch_redirect_response=True
        )

        response = self.client.get(reverse("profile"))
        self.assertRedirects(response, reverse("event_organizer_dashboard"))
