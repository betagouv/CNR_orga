from django.test import TestCase
from django.urls import reverse
from faker import Faker

from event.factories import BookingFactory, ContributionFactory, ContributionStatusFactory, EventFactory
from event.models import Contribution, ContributionStatus, Event
from signup.factories import EmailBasedUserFactory


faker = Faker("fr_FR")


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
            "place_name": event.place_name,
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
            "place_name": self.event.place_name,
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


class EventContributionCreateViewTest(TestCase):
    def setUp(self):
        self.event = EventFactory()
        self.url = reverse("event_organizer_contribution_create", kwargs={"event_pk": self.event.pk})
        self.detail_url = reverse("event_organizer_event_detail", kwargs={"pk": self.event.pk})
        self.user = self.event.owner

    def test_user_cannot_create_contribution(self):
        user = EmailBasedUserFactory(is_organizer=False)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_other_organizer_cannot_create_contribution(self):
        user = EmailBasedUserFactory(is_organizer=True)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_user_can_create_contribution(self):
        self.client.force_login(self.user)

        # Is there the create link in list view
        response = self.client.get(self.detail_url)
        self.assertContains(response, self.url)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # Is there the return link
        self.assertContains(response, "Retour à la liste des contributions")
        self.assertContains(response, self.detail_url)

        other_contribution = ContributionFactory.build()  # for generate data without save object
        other_contribution_status = ContributionStatusFactory.build()
        self.assertEqual(Contribution.objects.count(), 0)
        self.assertEqual(ContributionStatus.objects.count(), 0)

        tags_to_submit = faker.sentences(nb=3)
        data = {
            "kind": other_contribution.kind,
            "title": other_contribution.title,
            "description": other_contribution.description,
            "public": other_contribution.public,
            "status": other_contribution_status.status,
            "tags": ", ".join(tags_to_submit),
        }

        response = self.client.post(self.url, data=data, follow=True)
        self.assertRedirects(response, self.detail_url)
        contrib = Contribution.objects.first()
        self.assertContains(response, contrib.title, html=True)

        self.assertEqual(contrib.title, other_contribution.title)
        self.assertEqual(contrib.current_status.status, other_contribution_status.status)
        self.assertEqual(contrib.public, other_contribution.public)

        tags_list = [f"{tag}" for tag in contrib.tags.all()]
        self.assertEqual(tags_to_submit.sort(), tags_list.sort())

    def test_user_can_chain_contributions_creation(self):
        self.client.force_login(self.user)

        for _ in range(3):
            other_contribution = ContributionFactory.build()  # for generate data without save object
            other_contribution_status = ContributionStatusFactory.build()

            tags_to_submit = faker.sentences(nb=3)
            data = {
                "kind": other_contribution.kind,
                "title": other_contribution.title,
                "description": other_contribution.description,
                "public": other_contribution.public,
                "status": other_contribution_status.status,
                "tags": ", ".join(tags_to_submit),
                "submitandadd": "Enregistrer et ajouter une nouvelle contribution",
            }

            response = self.client.post(self.url, data=data, follow=True)
            self.assertRedirects(response, self.url)

        self.assertEqual(Contribution.objects.count(), 3)
        self.assertEqual(ContributionStatus.objects.count(), 3)


class EventContributionUpdateViewTest(TestCase):
    def setUp(self):
        self.contribution_status = ContributionStatusFactory()
        self.contribution = self.contribution_status.contribution
        self.url = reverse("event_organizer_contribution_update", kwargs={"pk": self.contribution.pk})
        self.detail_url = reverse("event_organizer_event_detail", kwargs={"pk": self.contribution.event.pk})
        self.user = self.contribution.event.owner

    def test_user_cannot_update_contribution(self):
        user = EmailBasedUserFactory(is_organizer=False)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_other_organizer_cannot_update_contribution(self):
        user = EmailBasedUserFactory(is_organizer=True)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_user_can_update_contribution(self):
        self.client.force_login(self.user)

        # Is there the update link in list view
        response = self.client.get(self.detail_url)
        self.assertContains(response, self.url)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        other_contribution = ContributionFactory.build()  # for other without save object
        self.assertEqual(Contribution.objects.count(), 1)
        self.assertEqual(ContributionStatus.objects.count(), 1)

        tags_to_submit = faker.sentences(nb=3)
        data = {
            "kind": self.contribution.kind,
            "title": other_contribution.title,
            "description": other_contribution.description,
            "public": self.contribution.public,
            "status": self.contribution.current_status.status,
            "tags": ", ".join(tags_to_submit),
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertRedirects(response, self.detail_url)
        self.assertContains(response, other_contribution.title, html=True)

        contrib = Contribution.objects.first()
        self.assertEqual(contrib.title, other_contribution.title)
        self.assertEqual(contrib.description, other_contribution.description)
        self.assertEqual(ContributionStatus.objects.count(), 1)

        tags_list = [f"{tag}" for tag in contrib.tags.all()]
        self.assertEqual(tags_to_submit.sort(), tags_list.sort())

        # Now, update status to see history and current status change
        first_status = self.contribution.current_status.status
        new_status = (
            ContributionStatus.Status.STUDY
            if first_status != ContributionStatus.Status.STUDY
            else ContributionStatus.Status.SELECT
        )
        data = {
            "kind": self.contribution.kind,
            "title": self.contribution.title,
            "description": self.contribution.description,
            "public": self.contribution.public,
            "status": new_status,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertRedirects(response, self.detail_url)
        self.assertEqual(ContributionStatus.objects.count(), 2)

        contrib = Contribution.objects.first()
        self.assertEqual(contrib.current_status.status, new_status)

        self.assertEqual(ContributionStatus.objects.first().status, first_status)
        self.assertEqual(ContributionStatus.objects.last().status, new_status)


class EventOrganizerAddViewTest(TestCase):
    def setUp(self):
        self.event = EventFactory()
        self.owner_user = self.event.owner

        self.guest_user_not_organizer = EmailBasedUserFactory(is_organizer=False)
        self.guest_user = EmailBasedUserFactory(is_organizer=True)

        self.detail_url = reverse("event_organizer_event_detail", kwargs={"pk": self.event.pk})
        self.add_url = reverse("event_organizer_event_add_organizer", kwargs={"event_pk": self.event.pk})

    def test_organizer_can_see_list_and_add_button(self):
        self.client.force_login(self.owner_user)
        response = self.client.get(self.detail_url)
        self.assertContains(response, self.add_url)
        self.assertContains(response, "Organisateurs (1)", html=True)
        self.assertContains(response, "Liste des organisateurs", html=True)
        self.assertContains(response, self.owner_user.email, html=True)
        self.assertContains(response, "Propriétaire", html=True)

    def test_organizer_cannot_add_invalid_email(self):
        self.client.force_login(self.owner_user)
        data = {
            "email_organizer": faker.text(10),
        }
        response = self.client.post(self.add_url, data=data)
        self.assertContains(response, "Saisissez une adresse de courriel valide.", html=True)

    def test_organizer_cannot_add_unknown_email(self):
        self.client.force_login(self.owner_user)
        data = {
            "email_organizer": faker.email(),
        }
        response = self.client.post(self.add_url, data=data)
        self.assertContains(response, "Cette adresse email ne correspond à aucun utilisateur.", html=True)

    def test_organizer_cannot_add_not_organizer_email(self):
        self.client.force_login(self.owner_user)
        data = {
            "email_organizer": self.guest_user_not_organizer.email,
        }
        response = self.client.post(self.add_url, data=data)
        self.assertContains(
            response, "Cette adresse email n'appartient pas à un utilisateur de type organisateur.", html=True
        )

    def test_organizer_can_add_organizer_email(self):
        self.client.force_login(self.owner_user)
        data = {
            "email_organizer": self.guest_user.email,
        }
        response = self.client.post(self.add_url, data=data, follow=True)
        self.assertRedirects(response, self.detail_url)
        self.assertContains(response, f"{self.guest_user} a été ajouté aux organisateurs avec succès.", html=True)

        # new added user can do anything on the event, but not add other organizer
        self.client.force_login(self.guest_user)

        response = self.client.get(reverse("event_organizer_dashboard"))
        self.assertContains(response, self.event.subject, html=True)

        response = self.client.get(self.detail_url)
        self.assertContains(response, "Organisateurs (2)", html=True)
        self.assertContains(response, "Liste des organisateurs", html=True)
        self.assertContains(response, self.guest_user.email, html=True)

        # guest organizer can update event
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
            "place_name": self.event.place_name,
            "address": self.event.address,
            "zip_code": self.event.zip_code,
            "city": self.event.city,
            "booking_online": self.event.booking_online,
            "participant_help": self.event.participant_help,
        }
        url_update_event = reverse("event_organizer_event_update", kwargs={"pk": self.event.pk})
        response = self.client.post(url_update_event, data=data)
        self.assertRedirects(response, self.detail_url)

        # guest organizer can add contribution
        other_contribution = ContributionFactory.build()  # for generate data without save object
        other_contribution_status = ContributionStatusFactory.build()
        tags_to_submit = faker.sentences(nb=3)
        data = {
            "kind": other_contribution.kind,
            "title": other_contribution.title,
            "description": other_contribution.description,
            "public": other_contribution.public,
            "status": other_contribution_status.status,
            "tags": ", ".join(tags_to_submit),
        }
        url_create_contribution = reverse("event_organizer_contribution_create", kwargs={"event_pk": self.event.pk})
        response = self.client.post(url_create_contribution, data=data, follow=True)
        self.assertRedirects(response, self.detail_url)
        contrib = Contribution.objects.first()
        self.assertContains(response, contrib.title, html=True)

        # but cannot add other organizer
        self.assertNotContains(response, self.add_url)
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 404)
