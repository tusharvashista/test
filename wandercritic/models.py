from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class User(AbstractUser):
    is_travel_agent = models.BooleanField(default=False)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=100, blank=True)
    company_website = models.URLField(blank=True)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

class TravelAgentApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, blank=True)
    experience = models.TextField(help_text="Describe your travel industry experience")
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Application by {self.full_name}"
    
    def approve(self):
        self.status = 'approved'
        self.user.is_travel_agent = True
        self.user.save()
        self.save()
    
    def reject(self):
        self.status = 'rejected'
        self.save()

class PlaceCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Place Categories"

class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Place(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_ratings = models.PositiveIntegerField(default=0)
    description = models.TextField()
    short_description = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='places/')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='places')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional fields
    history = models.TextField(blank=True)
    highlights = models.TextField(blank=True)  # Store as JSON list
    best_time_to_visit = models.TextField(blank=True)
    getting_there = models.TextField(blank=True)
    tips = models.TextField(blank=True)  # Store as JSON list
    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Estimated budget for the trip in GBP",
        null=True,
        blank=True
    )
    
    # Categories and Tags
    categories = models.ManyToManyField(PlaceCategory, related_name='places')
    tags = models.ManyToManyField(Tag, related_name='places')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('wandercritic:place_detail', kwargs={'slug': self.slug})

    def update_rating(self):
        reviews = self.review_set.all()
        if reviews:
            total = sum(review.rating for review in reviews)
            self.average_rating = total / len(reviews)
            self.total_ratings = len(reviews)
            self.save(update_fields=['average_rating', 'total_ratings'])

    @property
    def highlights_list(self):
        if self.highlights:
            return [h.strip() for h in self.highlights.split('\n') if h.strip()]
        return []

    @property
    def tips_list(self):
        if self.tips:
            return [t.strip() for t in self.tips.split('\n') if t.strip()]
        return []

    def __str__(self):
        return self.name

class PlaceImage(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='places/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.place.name}"

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['place', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}\'s review of {self.place.name}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.place.update_rating()

class Report(models.Model):
    REPORT_TYPES = [
        ('inappropriate', 'Inappropriate Content'),
        ('spam', 'Spam'),
        ('misinformation', 'Misinformation'),
        ('other', 'Other')
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed')
    ]
    
    CONTENT_TYPES = [
        ('place', 'Place'),
        ('user', 'User'),
        ('bug', 'Bug')
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports_filed')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='reports',null=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='place')
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                  related_name='resolved_reports')
    url = models.URLField()
    
    def resolve(self, admin_user):
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.resolved_by = admin_user
        self.save()
    
    def dismiss(self, admin_user):
        self.status = 'dismissed'
        self.resolved_at = timezone.now()
        self.resolved_by = admin_user
        self.save()
    
    def __str__(self):
        return f"Report by {self.reporter.username if self.reporter else 'Unknown'} on {self.place.name}"


class WebsiteReview(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    content = models.TextField()
    role = models.CharField(max_length=50)  # Will store 'User' or 'Travel Agent'
    created_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=True)  # For admin to control which reviews to show

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Website review by {self.user.username}'
