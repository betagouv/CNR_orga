from django.db import migrations


def _fill_first_organizer(apps, schema_editor):  # pylint: disable=unused-argument
    Event = apps.get_model("event", "Event")
    events = Event.objects.all()
    for event in events:
        event.organizers.add(event.owner)


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0011_event_synthesis"),
    ]

    operations = [
        migrations.RunPython(_fill_first_organizer, migrations.RunPython.noop, elidable=True),
    ]
