from django.conf import settings
import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('location', '0001_initial'),
    ]


    operations = [
        # Create SQL to create partitioned table for Accommodation
        migrations.RunSQL(
            """
            DROP TABLE IF EXISTS location_accommodation CASCADE;

            CREATE TABLE IF NOT EXISTS location_accommodation (
                id VARCHAR(20),
                feed SMALLINT,
                title VARCHAR(100) NOT NULL,
                country_code CHAR(2),
                bedroom_count INT,
                review_score NUMERIC(3, 1) DEFAULT 0,
                usd_rate NUMERIC(10, 2),
                center GEOMETRY(POINT),
                images TEXT[],
                location_id CHAR REFERENCES location_location(id) ON DELETE CASCADE,
                amenities TEXT[],
                user_id INT REFERENCES auth_user(id),
                published BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                PRIMARY KEY (id, feed)
            ) PARTITION BY LIST (feed);
            """,
            reverse_sql="DROP TABLE IF EXISTS location_accommodation;",
        ),

        # Create partitions for Accommodation table
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS location_accommodation_feed_0 PARTITION OF location_accommodation
            FOR VALUES IN (0);

            CREATE TABLE IF NOT EXISTS location_accommodation_feed_1 PARTITION OF location_accommodation
            FOR VALUES IN (1);

            CREATE TABLE IF NOT EXISTS location_accommodation_feed_2 PARTITION OF location_accommodation
            FOR VALUES IN (2);
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS location_accommodation_feed_0;
            DROP TABLE IF EXISTS location_accommodation_feed_1;
            DROP TABLE IF EXISTS location_accommodation_feed_2;
            """,
        ),
    ]
