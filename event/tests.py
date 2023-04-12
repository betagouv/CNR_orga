from django.test import TestCase
from django.urls import reverse

from event.factories import EventFactory
from event.models import Event
from signup.factories import EmailBasedUserFactory


class EventDashboardViewTest(TestCase):
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


class EventCreateViewTest(TestCase):
    def setUp(self):
        self.url = reverse("event_organizer_event_create")
        self.list_url = reverse("event_organizer_dashboard")
        self.user = EmailBasedUserFactory(is_organizer=True)

    def test_user_cannot_create_event(self):
        user = EmailBasedUserFactory(is_organizer=False)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_user_can_create_event(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        event = EventFactory.build()

        self.assertEqual(Event.objects.count(), 0)
        data = {
            "pub_status": event.pub_status,
            "theme": event.theme,
            "sub_theme": event.sub_theme,
            "subject": event.subject,
            "description": event.description,
            "scale": event.scale,
            "start_0": event.start.strftime("%Y-%m-%d"),
            "start_1": event.start.strftime("%H:%M"),
            "end_0": event.end.strftime("%Y-%m-%d"),
            "end_1": event.end.strftime("%H:%M"),
            "address": event.address,
            "zip_code": event.zip_code,
            "city": event.city,
            "booking_online": event.booking_online,
            "participant_help": event.participant_help,
        }
        response = self.client.post(self.url, data=data)
        self.assertRedirects(response, self.list_url)
        self.assertEqual(Event.objects.count(), 1)

        # event are now in dashboard
        response = self.client.get(self.list_url)
        self.assertContains(response, event.subject)


class EventUpdateViewTest(TestCase):
    def setUp(self):
        self.event = EventFactory()
        self.url = reverse("event_organizer_event_update", kwargs={"pk": self.event.pk})
        self.list_url = reverse("event_organizer_dashboard")
        self.user = self.event.owner

    def test_user_cannot_update_event(self):
        user = EmailBasedUserFactory(is_organizer=False)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_other_organizer_cannot_update_event(self):
        user = EmailBasedUserFactory(is_organizer=True)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_user_can_update_event(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        other_event = EventFactory.build()
        self.assertEqual(Event.objects.count(), 1)
        data = {
            "pub_status": self.event.pub_status,
            "theme": self.event.theme,
            "sub_theme": self.event.sub_theme,
            "subject": other_event.subject,
            "description": self.event.description,
            "scale": self.event.scale,
            "start_0": self.event.start.strftime("%Y-%m-%d"),
            "start_1": self.event.start.strftime("%H:%M"),
            "end_0": self.event.end.strftime("%Y-%m-%d"),
            "end_1": self.event.end.strftime("%H:%M"),
            "address": self.event.address,
            "zip_code": self.event.zip_code,
            "city": self.event.city,
            "booking_online": self.event.booking_online,
            "participant_help": self.event.participant_help,
        }
        response = self.client.post(self.url, data=data)
        self.assertRedirects(response, self.list_url)
        event_after = Event.objects.first()

        # Has the subject been updated?
        self.assertEqual(event_after.subject, other_event.subject)
