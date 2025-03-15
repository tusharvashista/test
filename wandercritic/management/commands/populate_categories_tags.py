from django.core.management.base import BaseCommand
from wandercritic.models import PlaceCategory, Tag
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Populates the database with predefined categories and tags'

    def handle(self, *args, **kwargs):
        # Clear existing categories
        PlaceCategory.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Cleared all existing categories'))

        # Main categories focused on Scotland and UK
        categories = [
            'Historic Castles & Palaces',  # Edinburgh Castle, Stirling Castle, etc.
            'Highland Landscapes',         # Scottish Highlands, Glencoe, etc.
            'Coastal & Islands',           # Isle of Skye, Hebrides, coastal towns
            'Cities & Urban',              # Edinburgh, Glasgow, Aberdeen
            'Lochs & Waterways',           # Loch Ness, Loch Lomond
            'Cultural Heritage',           # Museums, galleries, historical sites
            'Natural Parks & Gardens',      # Cairngorms, Trossachs
            'Whisky Distilleries',         # Speyside distilleries, whisky tours
            'Historic Sites',               # Battlefields, ancient ruins
            'Traditional Experiences'       # Highland games, ceilidhs, festivals
        ]

        # Popular travel tags
        tags = [
            # Accommodation
            'Hotels', 'Resorts', 'Hostels', 'Camping', 'Glamping',
            # Experience
            'Family-Friendly', 'Romantic', 'Solo Travel', 'Group Tours',
            'Off the Beaten Path', 'Hidden Gems', 'Must-See', 'Local Experience',
            # Activities
            'Surfing', 'Skiing', 'Snorkeling', 'Diving', 'Cycling',
            'Rock Climbing', 'Yoga', 'Meditation', 'Cooking Classes',
            # Features
            'Pet-Friendly', 'Wheelchair Accessible', 'Free WiFi', 'Pool',
            'Ocean View', 'Mountain View', 'City View',
            # Atmosphere
            'Peaceful', 'Bustling', 'Scenic', 'Historic', 'Modern',
            'Traditional', 'Trendy', 'Authentic',
            # Time
            'Weekend Getaway', 'Day Trip', 'Long Stay', 'Seasonal',
            # Special Interest
            'Photography Spots', 'Foodie Paradise', 'Shopping Haven',
            'Architecture', 'Art Scene', 'Music Scene', 'Night Markets',
            # Environment
            'Beach', 'Mountains', 'Desert', 'Jungle', 'Islands',
            'Lakes', 'Rivers', 'National Parks', 'UNESCO Sites',
            # Climate
            'Tropical', 'Mediterranean', 'Alpine', 'Desert Climate',
            # Budget Indicators
            'Budget', 'Mid-Range', 'Luxury', 'All-Inclusive'
        ]

        # Create categories
        for category_name in categories:
            category, created = PlaceCategory.objects.get_or_create(
                name=category_name,
                defaults={'slug': slugify(category_name)}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category_name}'))

        # Create tags
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': slugify(tag_name)}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created tag: {tag_name}'))

        self.stdout.write(self.style.SUCCESS('Successfully populated categories and tags'))
