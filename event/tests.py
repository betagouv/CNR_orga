from django.test import TestCase
from django.urls import reverse

from signup.factories import EmailBasedUserFactory


class EventDashboardTest(TestCase):
    def setUp(self):
        self.url = reverse("event_organizer_dashboard")

    def test_anonymous_user_cannot_see_dashboard_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{reverse("login")}?next={self.url}')

    def test_user_cannot_see_dashboard_page(self):
        user = EmailBasedUserFactory(is_organizer=False)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_organizer_user_can_see_dashboard_page(self):
        user = EmailBasedUserFactory(is_organizer=True)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
