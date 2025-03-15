from django.core.management.base import BaseCommand
from wandercritic.models import Place, PlaceCategory

class Command(BaseCommand):
    help = 'Migrates places to use new categories'

    def handle(self, *args, **kwargs):
        # Get all places
        places = Place.objects.all()
        self.stdout.write(f'Found {places.count()} places to process')

        # Get new categories
        categories = PlaceCategory.objects.all()
        if not categories.exists():
            self.stdout.write(self.style.ERROR('No categories found. Please run populate_categories_tags first.'))
            return

        # Default category (Cities & Urban)
        default_category = PlaceCategory.objects.filter(name='Cities & Urban').first()
        
        # Process each place
        for place in places:
            if not place.categories.exists():
                if default_category:
                    place.categories.add(default_category)
                    self.stdout.write(f'Added default category to place: {place.name}')
            
        self.stdout.write(self.style.SUCCESS('Successfully migrated place categories'))
