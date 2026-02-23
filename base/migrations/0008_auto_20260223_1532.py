from django.db import migrations

def delete_orphan_rooms(apps, schema_editor):
    Room = apps.get_model('base', 'Room')
    Room.objects.filter(host__isnull=True).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_auto_20260223_0237'),
    ]

    operations = [
        migrations.RunPython(delete_orphan_rooms),
    ]
