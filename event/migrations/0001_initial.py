# Generated by Django 4.1.7 on 2023-04-07 21:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "pub_status",
                    models.CharField(
                        choices=[("pub", "Public"), ("priv", "Privé"), ("unpub", "Non publié")],
                        default="unpub",
                        max_length=5,
                        verbose_name="Status de publication",
                    ),
                ),
                (
                    "theme",
                    models.CharField(
                        choices=[("sante", "Santé"), ("biodiv", "Biodiversité")],
                        max_length=6,
                        verbose_name="Thématique",
                    ),
                ),
                ("sub_theme", models.CharField(blank=True, max_length=100, null=True, verbose_name="Sous-thématique")),
                ("subject", models.CharField(blank=True, max_length=100, null=True, verbose_name="Sujet")),
                ("description", models.TextField(blank=True, null=True, verbose_name="Description")),
                (
                    "scale",
                    models.CharField(
                        choices=[
                            ("loc", "Locale"),
                            ("reg", "Régionale"),
                            ("dep", "Départementale"),
                            ("nat", "Nationale"),
                        ],
                        default="loc",
                        max_length=3,
                        verbose_name="Échelle",
                    ),
                ),
                ("start", models.DateTimeField(verbose_name="Date et heure de début")),
                ("end", models.DateTimeField(verbose_name="Date et heure de fin")),
                ("address", models.CharField(max_length=255, verbose_name="Adresse")),
                ("zip_code", models.CharField(max_length=5, verbose_name="Code postal")),
                ("city", models.CharField(max_length=255, verbose_name="Ville")),
                ("practical_information", models.TextField(blank=True, null=True, verbose_name="Infos pratiques")),
                (
                    "image",
                    models.ImageField(blank=True, null=True, upload_to="images", verbose_name="Image d'illustration"),
                ),
                ("booking_online", models.BooleanField(verbose_name="Inscription en ligne")),
                ("participant_help", models.BooleanField(verbose_name="Aide des participants")),
                ("planning", models.TextField(blank=True, null=True, verbose_name="Planning")),
                (
                    "organizers",
                    models.ManyToManyField(blank=True, related_name="event_organised", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_owned",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="",
                    ),
                ),
            ],
        ),
    ]