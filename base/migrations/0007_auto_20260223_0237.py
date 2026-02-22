from django.db import migrations

def delete_orphan_rooms(apps, schema_editor):
    Room = apps.get_model('base', 'Room')
    Room.objects.filter(host__isnull=True).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_alter_room_host'),
    ]

    operations = [
        migrations.RunPython(delete_orphan_rooms),
    ]