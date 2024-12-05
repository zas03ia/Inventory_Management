from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import Location, Accommodation, LocalizeAccommodation
from django.db import connection
from django.http import HttpResponse
from import_export import resources
from import_export.admin import ImportMixin


class LocationResource(resources.ModelResource):
    class Meta:
        model = Location
        fields = ('id', 'title', 'center', 'parent_id', 'location_type',
                  'country_code', 'state_abbr', 'city', 'created_at', 'updated_at')


@admin.register(Location)
class LocationAdmin(ImportMixin, OSMGeoAdmin):
    resource_class = LocationResource
    list_display = ('id', 'title', 'location_type',
                    'country_code', 'state_abbr', 'city', 'created_at')
    list_filter = ('location_type', 'country_code', 'state_abbr')
    search_fields = ('title', 'country_code', 'state_abbr', 'city')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Accommodation)
class AccommodationAdmin(OSMGeoAdmin):

    list_display = (
        "id",
        "title",
        "country_code",
        "bedroom_count",
        "review_score",
        "usd_rate",
        "published",
        "created_at",
    )
    list_filter = ("country_code", "bedroom_count", "published", "feed")
    search_fields = ("title", "country_code", "review_score", "amenities")
    readonly_fields = ("created_at", "updated_at", "user_id")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Allow superusers to access the full queryset
        if request.user.is_superuser:
            return qs

        # Show filtered queryset to a property owner
        elif request.user.groups.filter(name="Property Owners").exists():
            return qs.filter(user_id=request.user)

        return qs.none()

    def save_model(self, request, obj, form, change):
        # Ensure the user is set during saving
        if not obj.user_id:
            obj.user_id = request.user
        obj.save()

    def has_change_permission(self, request, obj=None):
        if obj and obj.user_id != request.user:
            return False
        return super().has_change_permission(request, obj)


@admin.register(LocalizeAccommodation)
class LocalizeAccommodationAdmin(admin.ModelAdmin):
    list_display = ('id', 'property_id', 'language')
    list_filter = ('language',)
    search_fields = ('property_id__title', 'language')
