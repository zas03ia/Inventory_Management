from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from location.models import Accommodation

class Command(BaseCommand):
    help = "Create 'Property Owners' group with specific permissions."

    def handle(self, *args, **kwargs):
        property_owners_group, created = Group.objects.get_or_create(name="Property Owners")
        accommodation_ct = ContentType.objects.get_for_model(Accommodation)
        view_permission = Permission.objects.get(content_type=accommodation_ct, codename="view_accommodation")
        add_permission = Permission.objects.get(content_type=accommodation_ct, codename="add_accommodation")
        change_permission = Permission.objects.get(content_type=accommodation_ct, codename="change_accommodation")
        property_owners_group.permissions.set([view_permission, add_permission, change_permission])
        self.stdout.write(self.style.SUCCESS("Property Owners group created successfully!"))
