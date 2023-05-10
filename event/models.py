from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property


class CurrentUpcomingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(start__gte=timezone.now())


class Event(models.Model):
    """
    An event being organised
    """

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


class Booking(models.Model):
    """
    Entry recording a user registration to an event
    """

    event = models.ForeignKey("Event", related_name="bookings", on_delete=models.CASCADE)
    participant = models.ForeignKey(get_user_model(), related_name="bookings", on_delete=models.CASCADE)
    offer_help = models.BooleanField(verbose_name="Proposer de l'aide", null=True)
    comment = models.TextField(verbose_name="Commentaire libre", null=True, blank=True)
    confirmed_on = models.DateTimeField(blank=True, null=True)
    cancelled_by = models.ForeignKey(
        get_user_model(),
        blank=True,
        null=True,
        related_name="cancelled_bookings",
        on_delete=models.SET_NULL,
    )
    cancelled_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("event", "participant")
        ordering = ["id"]


class Contribution(models.Model):
    """
    Entry recording contributions made during event
    """

    class Kind(models.TextChoices):
        PROPOSAL = "proposal", "Proposition"
        IDEA = "idea", "Idée"
        PROJECT = "project", "Projet"

    event = models.ForeignKey("Event", related_name="contribute", on_delete=models.CASCADE)
    kind = models.CharField(
        max_length=8,
        choices=Kind.choices,
        default=Kind.PROPOSAL,
        verbose_name="Nature",
    )
    title = models.CharField(max_length=250, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    public = models.BooleanField(verbose_name="Publique")

    # TODO: tag ?
    # TODO: document complémentaires

    @cached_property
    def current_status(self):
        return ContributionStatus.objects.filter(contribution=self).last()


class ContributionStatus(models.Model):
    class Status(models.TextChoices):
        UNSUCCESS = "uns", "Non retenue"
        STUDY = "stu", "En cours d'étude"
        SELECT = "sel", "Retenue"

    contribution = models.ForeignKey("Contribution", related_name="contribution_evolution", on_delete=models.CASCADE)
    change_on = models.DateField()
    status = models.CharField(
        max_length=5,
        choices=Status.choices,
        default=Status.STUDY,
        verbose_name="Statut",
    )
