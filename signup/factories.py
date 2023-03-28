import functools
import uuid

import factory
from django.contrib.auth.hashers import make_password

from signup.models import EmailBasedUser, OrganizerEmail


DEFAULT_PASSWORD = "P4ssw0rd!***"


@functools.cache
def default_password():
    return make_password(DEFAULT_PASSWORD)


class OrganizerEmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrganizerEmail

    email = factory.Faker("email")


class EmailBasedUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailBasedUser

    username = factory.LazyFunction(lambda: uuid.uuid4().hex)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    password = factory.LazyFunction(default_password)
