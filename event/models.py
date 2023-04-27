from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class CurrentUpcomingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(start__gte=timezone.now())


class Event(models.Model):
    class PubStatus(models.TextChoices):
        PUB = "pub", "Public"
        PRIV = "priv", "Privé"
        UNPUB = "unpub", "Non publié"

    class Theme(models.TextChoices):
        SANTE = "sante", "Santé"
        BIODIV = "biodiv", "Biodiversité"

    class Scale(models.TextChoices):
        LOC = "loc", "Locale"
        REG = "reg", "Régionale"
        DEP = "dep", "Départementale"
        NAT = "nat", "Nationale"

    owner = models.ForeignKey(
        get_user_model(),
        related_name="event_owned",
        on_delete=models.CASCADE,
        verbose_name="",
    )

    organizers = models.ManyToManyField(get_user_model(), blank=True, related_name="event_organised")

    pub_status = models.CharField(
        max_length=5,
        choices=PubStatus.choices,
        default=PubStatus.UNPUB,
        verbose_name="Status de publication",
    )

    theme = models.CharField(
        max_length=6,
        choices=Theme.choices,
        verbose_name="Thématique",
    )

    sub_theme = models.CharField(
        max_length=100,
        verbose_name="Sous-thématique",
        null=True,
        blank=True,
    )

    subject = models.CharField(
        max_length=100,
        verbose_name="Sujet",
        null=True,
        blank=True,
    )

    description = models.TextField(verbose_name="Description", null=True, blank=True)

    scale = models.CharField(
        max_length=3,
        choices=Scale.choices,
        default=Scale.LOC,
        verbose_name="Échelle",
    )

    start = models.DateTimeField(verbose_name="Date et heure de début")
    end = models.DateTimeField(verbose_name="Date et heure de fin")

    address = models.CharField(
        max_length=255,
        verbose_name="Adresse",
    )

    zip_code = models.CharField(
        max_length=5,
        verbose_name="Code postal",
    )

    city = models.CharField(
        max_length=255,
        verbose_name="Ville",
    )

    practical_information = models.TextField(verbose_name="Infos pratiques", null=True, blank=True)

    image = models.ImageField(verbose_name="Image d'illustration", upload_to="images", blank=True, null=True)

    booking_online = models.BooleanField(verbose_name="Inscription en ligne")

    # TODO: who and how many can booking

    participant_help = models.BooleanField(verbose_name="Aide des participants")

    planning = models.TextField(verbose_name="Planning", null=True, blank=True)

    # TODO: downloaded documents

    objects = models.Manager()
    current_and_upcomings = CurrentUpcomingManager()

    class Meta:
        verbose_name = "Concertation"
        verbose_name_plural = "Concertations"
        ordering = ["start", "end"]

    def __str__(self):
        return f"{self.theme} - {self.subject} - {self.start}"