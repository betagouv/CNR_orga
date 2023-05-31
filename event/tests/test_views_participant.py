from django.test import TestCase
from django.urls import reverse

from event.factories import ContributionFactory, EventFactory
from event.models import Booking, Contribution, Event
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

    def test_list_page_upcoming_filter(self):
        # list upcoming events
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


class ContributionListViewTest(TestCase):
    def setUp(self):
        self.url = reverse("contribution_list")
        self.biodiv_contributions = ContributionFactory.create_batch(
            2,
            event__theme=Event.Theme.BIODIV,
            event__pub_status=Event.PubStatus.PUB,
            public=True,
            tags=["tag1", "tag2"],
        )
        self.sante_contributions = ContributionFactory.create_batch(
            2,
            event__theme=Event.Theme.SANTE,
            event__pub_status=Event.PubStatus.PUB,
            public=True,
            tags=["tag3", "tag4"],
        )
        self.sante_private_contributions = ContributionFactory.create_batch(
            3, event__theme=Event.Theme.SANTE, public=False
        )
        self.sante_private_event_contributions = ContributionFactory.create_batch(
            3, event__theme=Event.Theme.SANTE, event__pub_status=Event.PubStatus.UNPUB, public=True
        )

    def test_anonymous_user_can_see_list_page(self):
        # list all public contributions
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        for contribution in self.biodiv_contributions + self.sante_contributions:
            self.assertContains(response, contribution.title, html=True)

        for contribution in self.sante_private_contributions + self.sante_private_event_contributions:
            self.assertNotContains(response, contribution.title, html=True)

    def test_list_page_theme_filter(self):
        # list filter by theme
        response = self.client.get(self.url, {"theme": Event.Theme.SANTE})
        for contribution in self.sante_contributions:
            self.assertContains(response, contribution.title, html=True)

        for contribution in self.biodiv_contributions + self.sante_private_contributions:
            self.assertNotContains(response, contribution.title, html=True)

    def test_list_page_scale_filter(self):
        scale = Contribution.objects.filter(public=True).first().event.scale
        response = self.client.get(self.url, {"scale": scale})
        contributions = Contribution.objects.filter(
            event__pub_status=Event.PubStatus.PUB, public=True, event__scale=scale
        )
        self.assertGreaterEqual(contributions.count(), 1)
        for contribution in contributions:
            self.assertContains(response, contribution.title, html=True)

        contributions = Contribution.objects.filter(event__pub_status=Event.PubStatus.PUB, public=True).exclude(
            event__scale=scale
        )
        self.assertGreaterEqual(contributions.count(), 1)
        for contribution in contributions:
            self.assertNotContains(response, contribution.title, html=True)

    def test_list_page_tag_filter(self):
        response = self.client.get(self.url, {"tag": "tag1"})
        self.assertEqual(response.status_code, 200)

        for contribution in self.biodiv_contributions:
            self.assertContains(response, contribution.title, html=True)

        for contribution in (
            self.sante_contributions + self.sante_private_contributions + self.sante_private_event_contributions
        ):
            self.assertNotContains(response, contribution.title, html=True)


class ContributionDetailViewTest(TestCase):
    def test_anonymous_user_cannot_see_not_public_contribution(self):
        contribution = ContributionFactory(public=False)
        url = reverse("contribution_detail", kwargs={"pk": contribution.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{reverse("login")}?next={url}')

    def test_anonymous_user_can_see_public_contribution(self):
        contribution = ContributionFactory(public=True)
        url = reverse("contribution_detail", kwargs={"pk": contribution.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
