from django.core.management.base import BaseCommand
from django.core.files import File
import requests
import json
import os
from wandercritic.models import Place, PlaceImage, User, Tag, PlaceCategory
from django.conf import settings
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Populate the database with places from JSON file'

    def handle(self, *args, **options):
        # Get the first travel agent user as the creator
        try:
            creator = User.objects.filter(is_travel_agent=True).first()
            if not creator:
                self.stdout.write(self.style.ERROR('No travel agent user found. Please create a travel agent user first.'))
                return
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
            return

        # Read the JSON file
        json_path = os.path.join(settings.BASE_DIR, 'wandercritic', 'fixtures', 'places.json')
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'JSON file not found at {json_path}'))
            return

        # Process each place
        for place_data in data['places']:
            # Check if place already exists
            existing_place = Place.objects.filter(name=place_data['name']).first()
            if existing_place:
                self.stdout.write(self.style.WARNING(f"Skipping existing place: {place_data['name']}"))
                continue

            # Create new place
            # First get or create the category
            category, _ = PlaceCategory.objects.get_or_create(name=place_data['category'])
            
            place = Place(
                name=place_data['name'],
                description=place_data['description'],
                short_description=place_data['short_description'],
                location=place_data['location'],
                created_by=creator,
                history=place_data.get('history', ''),
                best_time_to_visit=place_data.get('best_time_to_visit', ''),
                getting_there=place_data.get('getting_there', ''),
                tips=place_data.get('tips', []),
                budget=place_data.get('budget', None)
            )
            place.save()

            # Set the category
            place.category = category
            place.save()

            # Create highlights as a JSON field
            place.highlights = place_data['highlights']
            place.save()

            # Create tags
            for tag_name in place_data['tags']:
                slug = slugify(tag_name)
                tag, created = Tag.objects.get_or_create(
                    slug=slug,
                    defaults={'name': tag_name}
                )
                place.tags.add(tag)

            # Download and save image
            if place_data['image_url']:
                try:
                    # Download image
                    response = requests.get(place_data['image_url'])
                    response.raise_for_status()

                    # Create image filename using place name
                    image_name = f"{place.name.replace(' ', '_').lower()}.jpg"
                    image_path = os.path.join(settings.MEDIA_ROOT, 'places', image_name)

                    # Save image to media directory
                    os.makedirs(os.path.dirname(image_path), exist_ok=True)
                    with open(image_path, 'wb') as f:
                        f.write(response.content)

                    # Create PlaceImage
                    with open(image_path, 'rb') as f:
                        image_file = File(f)
                        # Set the file name to a relative path (relative to MEDIA_ROOT)
                        image_file.name = os.path.join('places', image_name)
                        place_image = PlaceImage(
                            place=place,
                            image=image_file,
                            caption=place.name,
                            is_primary=True
                        )
                        place_image.save()

                    self.stdout.write(self.style.SUCCESS(f"Successfully added {place.name} with image"))

                except requests.RequestException as e:
                    self.stdout.write(self.style.WARNING(f"Could not download image for {place.name}: {str(e)}"))
                    self.stdout.write(self.style.SUCCESS(f"Successfully added {place.name} without image"))

        self.stdout.write(self.style.SUCCESS("Database population complete!"))
