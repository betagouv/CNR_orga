from django import forms
from django.forms.fields import SplitDateTimeField
from django.forms.models import ModelForm

from event.models import Event


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
        (Event.PubStatus.PUB, "Oui (public - en accès à tous)"),
        (Event.PubStatus.PRIV, "Non (privée - sur lien seul)"),
    ]
    pub_status = forms.ChoiceField(
        label="Souhaitez-vous rendre public cette page sur le site du CNR ?",
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
        label="Souhaitez-vous que les participants puissent vous proposer de l'aide lors de la concertation",
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
            "practical_information": "Infos pratiques pour s'y rendre si nécessaire",
        }


class EventListFilterForm(forms.Form):
    theme = forms.ChoiceField(
        label="Thématique",
        choices=[("", "Selectionner une thématique")] + Event.Theme.choices,
        widget=forms.Select(
            attrs={
                "class": "fr-select",
                "onchange": "this.form.submit()",
            }
        ),
    )
    scale = forms.ChoiceField(
        label="Échelle",
        choices=[("", "Selectionner une échelle")] + Event.Scale.choices,
        widget=forms.Select(
            attrs={
                "class": "fr-select",
                "onchange": "this.form.submit()",
            }
        ),
    )
