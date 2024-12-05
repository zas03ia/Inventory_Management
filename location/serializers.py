from rest_framework import serializers

# Create your tests here.
from django.contrib.auth.models import User, Group
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        # Create user and add them to the "Property Owners" group
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        # Add user to the "Property Owners" group
        property_owners_group, created = Group.objects.get_or_create(name="Property Owners")
        user.groups.add(property_owners_group)
        return user