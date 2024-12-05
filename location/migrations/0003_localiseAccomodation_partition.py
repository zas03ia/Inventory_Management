from django.conf import settings
import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('location', '0002_accommodation_partition'),
    ]


    operations = [
        # Create partitioned table for LocalizeAccommodation
        migrations.RunSQL(
            """
            DROP TABLE IF EXISTS location_localizeaccommodation CASCADE;
            CREATE TABLE IF NOT EXISTS location_localizeaccommodation (
                id SERIAL,
                property_id VARCHAR,
                feed SMALLINT,
                language CHAR(2),
                description TEXT,
                policy JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id, language),  -- Include the partitioning column 'language' in the PRIMARY KEY
                UNIQUE (property_id, feed, language),  -- Ensure unique constraint also includes 'language'
                FOREIGN KEY (property_id, feed) REFERENCES location_accommodation(id, feed) ON DELETE CASCADE
            ) PARTITION BY LIST (language);
            """,
            reverse_sql="DROP TABLE IF EXISTS location_localizeaccommodation;",
        ),

        # Create partitions for LocalizeAccommodation table
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS location_localizeaccommodation_en PARTITION OF location_localizeaccommodation FOR VALUES IN ('en');
            CREATE TABLE IF NOT EXISTS location_localizeaccommodation_fr PARTITION OF location_localizeaccommodation FOR VALUES IN ('fr');
            CREATE TABLE IF NOT EXISTS location_localizeaccommodation_de PARTITION OF location_localizeaccommodation FOR VALUES IN ('de');
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS location_localizeaccommodation_en;
            DROP TABLE IF EXISTS location_localizeaccommodation_fr;
            DROP TABLE IF EXISTS location_localizeaccommodation_de;
            """,
        ),
    ]
