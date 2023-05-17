from django.test import TestCase
from django.urls import reverse

from event.factories import EventFactory
from event.models import Booking, Event
from signup.factories import EmailBasedUserFactory


class EventListViewTest(TestCase):
    def setUp(self):
        self.url = reverse("event_list")
        self.upcoming_events = EventFactory.create_batch(5, upcoming=True, pub_status=Event.PubStatus.PUB)
        self.upcoming_priv_events = EventFactory.create_batch(2, upcoming=True, pub_status=Event.PubStatus.PRIV)
        self.past_events = EventFactory.create_batch(10, past=True, pub_status=Event.PubStatus.PUB)
        self.past_priv_events = EventFactory.create_batch(4, past=True, pub_status=Event.PubStatus.PRIV)

    def test_anonymous_user_can_see_list_page(self):
        # list all public events
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        for event in self.upcoming_events + self.past_events:
            self.assertContains(response, event.subject, html=True)

        for event in self.upcoming_priv_events + self.past_priv_events:
            self.assertNotContains(response, event.subject, html=True)

    def test_list_page_upcomin_filter(self):
        # list incoming events
        response = self.client.get(self.url, {"upcoming": "on"})
        for event in self.upcoming_events:
            self.assertContains(response, event.subject, html=True)

        for event in self.past_events + self.upcoming_priv_events + self.past_priv_events:
            self.assertNotContains(response, event.subject, html=True)

    def test_list_page_theme_filter(self):
        theme = Event.objects.filter(pub_status=Event.PubStatus.PUB).first().theme
        response = self.client.get(self.url, {"theme": theme})

        events = Event.objects.filter(pub_status=Event.PubStatus.PUB, theme=theme)
        self.assertGreaterEqual(events.count(), 1)
        for event in events:
            self.assertContains(response, event.subject, html=True)

        events = Event.objects.filter(pub_status=Event.PubStatus.PUB).exclude(theme=theme)
        self.assertGreaterEqual(events.count(), 1)
        for event in events:
            self.assertNotContains(response, event.subject, html=True)

    def test_list_page_scale_filter(self):
        scale = Event.objects.filter(pub_status=Event.PubStatus.PUB).first().scale
        response = self.client.get(self.url, {"scale": scale})
        events = Event.objects.filter(pub_status=Event.PubStatus.PUB, scale=scale)
        self.assertGreaterEqual(events.count(), 1)
        for event in events:
            self.assertContains(response, event.subject, html=True)

        events = Event.objects.filter(pub_status=Event.PubStatus.PUB).exclude(scale=scale)
        self.assertGreaterEqual(events.count(), 1)
        for event in events:
            self.assertNotContains(response, event.subject, html=True)


class EventRegistrationViewTest(TestCase):
    def setUp(self):
        self.event = EventFactory()
        self.event_url = reverse("event_detail", kwargs={"pk": self.event.pk})
        self.register_url = reverse("event_registration", kwargs={"pk": self.event.pk})
        self.user = EmailBasedUserFactory(is_organizer=False)

    def test_user_can_register_for_the_event(self):
        self.client.force_login(self.user)
        response = self.client.get(self.event_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Participer")
        self.assertContains(response, self.register_url)
        self.assertNotContains(response, "Se désinscrire")

        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.objects.count(), 0)

        data = {"offer_help": False, "comment": ""}
        response = self.client.post(self.register_url, data, follow=True)
        self.assertRedirects(response, self.event_url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Booking.objects.count(), 1)
        booking = Booking.objects.get(event=self.event, participant=self.user)
        unregister_link = reverse("event_registration_delete", kwargs={"pk": booking.pk})
        self.assertContains(response, "Se désinscrire")
        self.assertContains(response, unregister_link)
        self.assertNotContains(response, "Participer")

        response = self.client.get(unregister_link)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.objects.count(), 1)

        response = self.client.post(unregister_link, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.objects.count(), 0)
        self.assertContains(response, "Participer")
        self.assertContains(response, self.register_url)
        self.assertNotContains(response, "Se désinscrire")
