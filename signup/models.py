from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class OrganizerEmail(models.Model):
    email = models.EmailField(_("email address"), unique=True)

    def __str__(self):
        return self.email


class EmailBasedUser(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    is_organizer = models.BooleanField("Est organisateur ?", default=False)

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
