from datetime import datetime, timezone

import factory
import factory.fuzzy
from dateutil.relativedelta import relativedelta

from event.models import Booking, Contribution, ContributionStatus, Event
from signup.factories import EmailBasedUserFactory


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    owner = factory.SubFactory(EmailBasedUserFactory, is_organizer=True)
    pub_status = factory.fuzzy.FuzzyChoice([Event.PubStatus.PUB, Event.PubStatus.PRIV])
    theme = factory.fuzzy.FuzzyChoice(Event.Theme.values)
    sub_theme = factory.Faker("sentence", nb_words=3, locale="fr_FR")
    subject = factory.Faker("sentence", nb_words=4, locale="fr_FR")
    description = factory.Faker("text", locale="fr_FR")
    scale = factory.fuzzy.FuzzyChoice(Event.Scale.values)
    start = factory.fuzzy.FuzzyDateTime(
        datetime.now(timezone.utc), datetime.now(timezone.utc) + relativedelta(years=2)
    )
    end = factory.LazyAttribute(lambda obj: obj.start + relativedelta(hours=4))

    place_name = factory.Faker("sentence", nb_words=3, locale="fr_FR")
    address = factory.Faker("address", locale="fr_FR")
    zip_code = factory.Faker("postcode", locale="fr_FR")
    city = factory.Faker("city", locale="fr_FR")
    booking_online = True
    participant_help = True

    @factory.post_generation
    def organizers(self, create, extracted, **kwargs):
        if not create:
            return

        self.organizers.add(self.owner)
        if extracted:
            self.organizers.add(*extracted)

    class Params:
        upcoming = factory.Trait(
            start=factory.fuzzy.FuzzyDateTime(
                datetime.now(timezone.utc) + relativedelta(days=1), datetime.now(timezone.utc) + relativedelta(years=2)
            ),
            end=factory.LazyAttribute(lambda obj: obj.start + relativedelta(hours=4)),
        )

        past = factory.Trait(
            start=factory.fuzzy.FuzzyDateTime(
                datetime.now(timezone.utc) - relativedelta(years=1), datetime.now(timezone.utc)
            ),
            end=factory.LazyAttribute(lambda obj: obj.start + relativedelta(hours=4)),
        )


class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Booking

    event = factory.SubFactory(EventFactory)
    participant = factory.SubFactory(EmailBasedUserFactory)
    offer_help = factory.Faker("pybool")
    comment = factory.Faker("text", locale="fr_FR")

    class Params:
        confirmed = factory.Trait(
            confirmed_on=factory.fuzzy.FuzzyDateTime(
                datetime.now(timezone.utc) - relativedelta(years=2), datetime.now(timezone.utc)
            )
        )
        cancelled = factory.Trait(
            cancelled_by=factory.SubFactory(EmailBasedUserFactory, is_organizer=True),
            cancelled_on=factory.fuzzy.FuzzyDateTime(
                datetime.now(timezone.utc) - relativedelta(years=2), datetime.now(timezone.utc)
            ),
        )


class ContributionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contribution

    event = factory.SubFactory(EventFactory)
    kind = factory.fuzzy.FuzzyChoice(Contribution.Kind.values)
    title = factory.Faker("sentence", nb_words=4, locale="fr_FR")
    description = factory.Faker("text", locale="fr_FR")
    public = factory.Faker("pybool")

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.tags.add(*extracted)


class ContributionStatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContributionStatus

    contribution = factory.SubFactory(ContributionFactory)
    change_on = factory.fuzzy.FuzzyDateTime(
        datetime.now(timezone.utc) - relativedelta(years=2), datetime.now(timezone.utc)
    )
    status = factory.fuzzy.FuzzyChoice(ContributionStatus.Status.values)
