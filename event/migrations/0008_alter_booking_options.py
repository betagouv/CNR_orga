# Generated by Django 4.1.9 on 2023-05-23 12:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0007_contribution_tags"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="booking",
            options={"ordering": ["id"], "verbose_name": "Participation", "verbose_name_plural": "Participations"},
        ),
    ]
