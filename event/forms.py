from django import forms
from django.forms.fields import SplitDateTimeField
from django.forms.models import ModelForm
from django.utils import timezone

from event.models import Booking, Contribution, ContributionStatus, Event


class MySplitDateTimeField(SplitDateTimeField):
    """A field with separate date and time elements and using HTML5 input types"""

    def __init__(self, *args, **kwargs):
        super(MySplitDateTimeField, self).__init__(*args, **kwargs)
        self.widget.widgets[0].input_type = "date"
        self.widget.widgets[1].input_type = "time"


class EventForm(ModelForm):
    start = MySplitDateTimeField(
        label="Date et heure de début",
        required=True,
    )
    end = MySplitDateTimeField(
        label="Date et heure de fin",
        required=True,
    )

    PUB_CHOICES = [
        (Event.PubStatus.PUB, "Oui (publique - en accès à tous)"),
        (Event.PubStatus.PRIV, "Non (privée - sur lien seul)"),
    ]
    pub_status = forms.ChoiceField(
        label="Souhaitez-vous rendre publique cette page sur le site du CNR ?",
        widget=forms.RadioSelect,
        choices=PUB_CHOICES,
    )

    booking_online = forms.NullBooleanField(
        label="Possibilité de s'inscrire en ligne ? (bouton visible sur la page)",
        widget=forms.RadioSelect(
            choices=[
                (True, "Oui"),
                (False, "Non"),
            ]
        ),
    )

    participant_help = forms.NullBooleanField(
        label="Possibilité pour les participants de s'inscrire également en tant que bénévoles ?",
        widget=forms.RadioSelect(
            choices=[
                (True, "Oui"),
                (False, "Non"),
            ]
        ),
    )

    class Meta:
        model = Event
        fields = [
            "pub_status",
            "theme",
            "sub_theme",
            "subject",
            "description",
            "scale",
            "start",
            "end",
            "place_name",
            "address",
            "zip_code",
            "city",
            "practical_information",
            "image",
            "booking_online",
            "participant_help",
            "planning",
        ]
        labels = {
            "theme": "Thématique du CNR",
            "subject": "Quel est le sujet de votre concertation ?",
            "description": "Décrivez votre concertation",
            "scale": "À quelle échelle se situe votre concertation ?",
            "practical_information": "Informations pratiques complémentaires",
            "place_name": "Nom du lieu",
        }


class EventListFilterForm(forms.Form):
    theme = forms.ChoiceField(
        label="Thématique",
        choices=[("", "Toutes")] + Event.Theme.choices,
        widget=forms.Select(
            attrs={
                "class": "fr-select",
                "onchange": "this.form.submit()",
            }
        ),
    )
    scale = forms.ChoiceField(
        label="Échelle",
        choices=[("", "Toutes")] + Event.Scale.choices,
        widget=forms.Select(
            attrs={
                "class": "fr-select",
                "onchange": "this.form.submit()",
            }
        ),
    )

    upcoming = forms.BooleanField(
        label="À venir uniquement",
        widget=forms.CheckboxInput(
            attrs={
                "onchange": "this.form.submit()",
            }
        ),
    )


class EventRegistrationForm(ModelForm):
    offer_help = forms.NullBooleanField(
        label="Souhaitez-vous proposer votre aide (facilitation, restitution, autre) ?",
        widget=forms.RadioSelect(
            choices=[
                (True, "Oui"),
                (False, "Non"),
            ]
        ),
    )

    class Meta:
        model = Booking
        fields = [
            "offer_help",
            "comment",
        ]


class ContributionForm(ModelForm):
    public = forms.BooleanField(
        label="Contribution publique ?",
        help_text="Publique : en accès à tous",
        widget=forms.CheckboxInput(
            attrs={
                "class": "fr-toggle__input",
            }
        ),
        required=False,
    )

    status = forms.ChoiceField(
        label="Quel est le statut de la contribution",
        choices=ContributionStatus.Status.choices,
    )

    class Meta:
        model = Contribution
        fields = ["kind", "title", "description", "public", "status", "tags"]

        labels = {
            "kind": "Quelle est la nature de la contribution",
            "title": "Quel est le titre de la contribution",
            "description": "Décrivez la contribution",
        }

    def save(self, commit=True):
        contribution = super().save(commit)
        new_status = self.cleaned_data.get("status")

        # if creation or status change
        if not contribution.current_status or contribution.current_status.status != new_status:
            ContributionStatus.objects.create(
                contribution=contribution,
                change_on=timezone.now().date(),
                status=new_status,
            )
        return contribution
