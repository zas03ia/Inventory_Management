import json
from django.core.management.base import BaseCommand
from location.models import Location

class Command(BaseCommand):
    help = "Generate a sitemap.json file for all country locations"

    def handle(self, *args, **kwargs):
        # Fetch all country locations
        countries = Location.objects.filter(location_type="country").order_by("title")

        sitemap = []
        for country in countries:
            # Create entry for each country
            country_data = {
                country.title: country.country_code.lower(),
                "locations": [],
            }
            
            # Fetch states and cities under each country
            states = Location.objects.filter(parent_id=country).order_by("title")
            for state in states:
                state_slug = f"{country.country_code.lower()}/{state.title.lower().replace(' ', '-')}"
                state_data = {state.title: state_slug}
                country_data["locations"].append(state_data)
            
            sitemap.append(country_data)

        # Write the sitemap to a JSON file
        with open("sitemap.json", "w", encoding="utf-8") as f:
            json.dump(sitemap, f, indent=4)
        
        self.stdout.write(self.style.SUCCESS("sitemap.json generated successfully!"))
