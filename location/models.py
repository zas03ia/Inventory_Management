from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from .middleware import get_current_user


class Location(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=100)
    center = models.PointField()
    parent_id = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)
    location_type = models.CharField(max_length=20)
    country_code = models.CharField(max_length=2)
    state_abbr = models.CharField(max_length=3, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.location_type == "country":
            return f"{self.title} ({self.country_code})"
        elif self.location_type == "state" or self.location_type == "province":
            return f"{self.title}, {self.country_code} ({self.state_abbr})"
        elif self.location_type == "city":
            return f"{self.city}, {self.state_abbr}, {self.country_code}"
        return self.title


class Accommodation(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    feed = models.PositiveSmallIntegerField(default=0)
    title = models.CharField(max_length=100, blank=False, null=False)
    country_code = models.CharField(max_length=2)
    bedroom_count = models.PositiveIntegerField()
    review_score = models.DecimalField(
        max_digits=3, decimal_places=1, default=0)
    usd_rate = models.DecimalField(max_digits=10, decimal_places=2)
    center = models.PointField()
    images = ArrayField(
        models.FileField(upload_to='media/', max_length=300),
        blank=True,
        default=list
    )
    location_id = models.ForeignKey(
        Location, on_delete=models.CASCADE, db_column='location_id')
    amenities = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list
    )
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, db_column='user_id')
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.user_id and get_current_user():
            self.user_id = get_current_user()
        super().save(*args, **kwargs)


class LocalizeAccommodation(models.Model):
    id = models.AutoField(primary_key=True)
    property_id = models.ForeignKey(
        Accommodation, on_delete=models.CASCADE, db_column='property_id')
    language = models.CharField(max_length=2)
    description = models.TextField()
    policy = models.JSONField()
