import os
from django.urls import reverse
from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from django.contrib.auth.models import Group, User
from location.models import Location, Accommodation
from location.middleware import get_current_user, CurrentUserMiddleware, _user
from django.http import HttpRequest


class ManagementCommandTests(TestCase):
    def test_create_groups_command(self):
        """Test the 'create_property_owners_group' management command."""
        call_command('create_property_owners_group')
        group = Group.objects.filter(name="Property Owners").first()
        self.assertIsNotNone(group)
        permissions = group.permissions.all()
        self.assertTrue(permissions.filter(codename="view_accommodation").exists())
        self.assertTrue(permissions.filter(codename="add_accommodation").exists())
        self.assertTrue(permissions.filter(codename="change_accommodation").exists())


    def test_generate_sitemap_command(self):
        """Test the 'generate_sitemap' management command."""
        # Setup test data
        country = Location.objects.create(
            id="1",
            title="Country Test",
            center="POINT(-56.5795 36.8283)",
            location_type="country",
            country_code="US",
            state_abbr=None,
            city=None,
            parent_id=None
        )
        state = Location.objects.create(
            id="2",
            title="State Test",
            center="POINT(-98.5795 49.8283)",
            location_type="state",
            country_code="US",
            state_abbr=None,
            city=None,
            parent_id=country
        )
        city = Location.objects.create(
            id="3",
            title="City Test",
            center="POINT(-25.5795 45.8283)",
            location_type="city",
            country_code="US",
            state_abbr=None,
            city=None,
            parent_id=state
        )

        # Redirect stdout to capture command output
        out = StringIO()
        call_command('generate_sitemap', stdout=out)
        
        # Check if the sitemap file is generated
        sitemap_path = os.path.join(os.getcwd(), 'sitemap.json')
        self.assertTrue(os.path.exists(sitemap_path))
        # Verify sitemap content
        with open(sitemap_path, 'r') as file:
            content = file.read()
            self.assertIn("Country Test", content)
            self.assertIn("State Test", content)
            self.assertNotIn("City Test", content)

        # Clean up
        os.remove(sitemap_path)


class ModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="password")
        self.user2 = User.objects.create_user(username="testuser2", password="password")
        self.superuser = User.objects.create_superuser(username="admin", password="password")

    def test_location_model(self):
        """Test Location model hierarchy."""
        country = Location.objects.create(
            id="1",
            title="Country Test",
            center="POINT(-56.5795 36.8283)",
            location_type="country",
            country_code="US",
            state_abbr=None,
            city=None,
            parent_id=None
        )
        state = Location.objects.create(
            id="2",
            title="State Test",
            center="POINT(-98.5795 49.8283)",
            location_type="state",
            country_code="US",
            state_abbr=None,
            city=None,
            parent_id=country
        )
        city = Location.objects.create(
            id="3",
            title="City Test",
            center="POINT(-25.5795 45.8283)",
            location_type="city",
            country_code="US",
            state_abbr=None,
            city=None,
            parent_id=state
        )

        self.assertEqual(city.parent_id, state)
        self.assertEqual(state.parent_id, country)
        self.assertEqual(country.parent_id, None)

    def test_accommodation_queryset(self):
        """Test Accommodation model queryset for superusers and regular users."""
        self.client.login(username="testuser1", password="password")
        accommodation = Accommodation.objects.create(feed=1, title="Test Accommodation", user_id=self.user1)
        accommodations = Accommodation.objects.filter(user_id=self.user1)
        self.assertIn(accommodation, accommodations)

        # Superuser should see all accommodations
        self.client.login(username="admin", password="password")
        accommodations = Accommodation.objects.all()
        self.assertIn(accommodation, accommodations)

        # Regular user with no permissions should see none
        self.client.login(username="testuser2", password="password")
        accommodations = Accommodation.objects.filter(user_id=self.user2)
        self.assertNotIn(accommodation, accommodations)

class MiddlewareTests(TestCase):
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # Initialize the middleware
        self.middleware = CurrentUserMiddleware(get_response=lambda request: None)


    def test_CurrentUserMiddleware(self):
        """Test that CurrentUserMiddleware sets the current user."""
        user = User.objects.create_user(username="testuser1", password="password", is_staff=True)
        self.client.login(username="testuser1", password="password")

        # Access the admin page or any page that triggers middleware processing
        response = self.client.get('/admin/')
        
        # The current user should be set in the request object by the middleware
        self.assertEqual(response.status_code, 200)

        # Use request.user to check if the middleware correctly set the user
        self.assertEqual(response.wsgi_request.user, user)

    def test_CurrentUserMiddleware_current_user_set_in_local_storage(self):
        # Create a mock request and set the user
        request = HttpRequest()
        request.user = self.user
        
        # Apply the middleware
        self.middleware(request)
        
        # Check if the user is set in the _user local storage
        self.assertEqual(_user.user, self.user)

    def test_CurrentUserMiddleware_current_user_is_none_for_anonymous_user(self):
        # Create a request with an anonymous user
        request = HttpRequest()
        request.user = None
        
        # Apply the middleware
        self.middleware(request)
        
        # Check if the _user.user is None
        self.assertIsNone(_user.user)

    def test_current_user_persists_between_requests(self):
        # Create a request with a test user
        request = HttpRequest()
        request.user = self.user
        
        # Apply the middleware once
        self.middleware(request)
        
        # Get the current user
        user_from_middleware = get_current_user()
        
        # Check that the user is the one set in the middleware
        self.assertEqual(user_from_middleware, self.user)

class AdminTests(TestCase):
    def setUp(self):
        # Set up the admin user and login
        self.admin_user = User.objects.create_superuser(username='admin', password='password')
        self.client.login(username='admin', password='password')

    def test_admin_import(self):
        """Test import functionality in the admin."""
        with open('example_location.csv', 'rb') as file:
            
            response = self.client.post(reverse('admin:location_location_import'), {
                'import_file_name': file,
                'original_file_name': 'test_import.csv',
                'format': 0,
                'resource': 'location.location',
            })

        self.assertEqual(response.status_code, 200)

    def test_check_partition_status_no_records(self):
        """Test that the partition status page shows 'No records found in this partition' when a partition has no data."""
        # Assume partition exists but no records in that partition
        response = self.client.get(reverse('admin:location_accommodation_changelist'))
        
        # Ensure that we see the "No records found" message for any partition with no data
        self.assertIn('0 accommodations', str(response.content))



