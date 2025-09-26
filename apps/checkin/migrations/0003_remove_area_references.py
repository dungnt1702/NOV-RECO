# Generated manually to remove area references

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkin', '0002_checkin_location'),
    ]

    operations = [
        # Drop index for area_id first
        migrations.RunSQL(
            sql="DROP INDEX IF EXISTS checkin_checkin_area_id_9b9239af;",
            reverse_sql="-- Cannot recreate index",
        ),
        
        # Remove area_id column from checkin_checkin table
        migrations.RunSQL(
            sql="ALTER TABLE checkin_checkin DROP COLUMN area_id;",
            reverse_sql="ALTER TABLE checkin_checkin ADD COLUMN area_id INTEGER;",
        ),
        
        # Drop area_area table
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS area_area;",
            reverse_sql="-- Cannot recreate area_area table",
        ),
    ]
