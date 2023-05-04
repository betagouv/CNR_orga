from django.test import TestCase
from django.urls import reverse

from event.factories import BookingFactory, EventFactory
from event.models import Booking, Event
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


class EventDetailViewTest(TestCase):
    def setUp(self):
        self.event = EventFactory()
        self.url = reverse("event_organizer_event_detail", kwargs={"pk": self.event.pk})

    def test_organizer_participant_list(self):
        bookings = BookingFactory.create_batch(10, event=self.event)
        self.client.force_login(self.event.owner)
        response = self.client.get(self.url)
        self.assertContains(response, "Participants (10)")
        self.assertContains(response, bookings[6].participant.first_name)
        self.assertContains(response, bookings[6].participant.last_name)

    def test_organizer_participant_accept(self):
        booking = BookingFactory(event=self.event)
        self.client.force_login(self.event.owner)
        response = self.client.get(self.url)
        self.assertContains(response, booking.participant.first_name)
        self.assertContains(response, booking.participant.last_name)
        self.assertContains(response, "En attente de confirmation")

        accept_url = reverse("event_organizer_registration_accept", kwargs={"pk": booking.pk})
        response = self.client.post(accept_url)
        self.assertContains(response, booking.participant.first_name)
        self.assertContains(response, booking.participant.last_name)
        self.assertContains(response, "Confirmée le ")

        response = self.client.get(self.url)
        self.assertContains(response, booking.participant.first_name)
        self.assertContains(response, booking.participant.last_name)
        self.assertContains(response, "Confirmée le ")

    def test_organizer_participant_decline(self):
        booking = BookingFactory(event=self.event)
        self.client.force_login(self.event.owner)
        response = self.client.get(self.url)
        self.assertContains(response, booking.participant.first_name)
        self.assertContains(response, booking.participant.last_name)
        self.assertContains(response, "En attente de confirmation")

        accept_url = reverse("event_organizer_registration_decline", kwargs={"pk": booking.pk})
        response = self.client.post(accept_url)
        self.assertContains(response, booking.participant.first_name)
        self.assertContains(response, booking.participant.last_name)
        self.assertContains(response, "Déclinée le ")

        response = self.client.get(self.url)
        self.assertContains(response, booking.participant.first_name)
        self.assertContains(response, booking.participant.last_name)
        self.assertContains(response, "Déclinée le ")


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

        other_event = EventFactory.build()  # for another subject without save object
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
        detail_url = reverse("event_organizer_event_detail", kwargs={"pk": self.event.pk})
        self.assertRedirects(response, detail_url)
        event_after = Event.objects.first()

        # Has the subject been updated?
        self.assertEqual(event_after.subject, other_event.subject)


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
