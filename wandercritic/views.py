from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.db.models import Avg
from .models import Place, PlaceImage, TravelAgentApplication, Report, Review, PlaceCategory, Tag, WebsiteReview
from .forms import (PlaceForm, PlaceImageForm, TravelAgentApplicationForm, ReportForm, ReportReviewForm, BugReportForm,
    WebsiteReviewForm, UserProfileForm, TravelAgentProfileForm, PasswordChangeForm)
from django.core.paginator import Paginator
from urllib.parse import urlparse

def is_superuser(user):
    return user.is_superuser

def index(request):
    places = Place.objects.annotate(
        avg_rating=Avg('review__rating')
    ).order_by('-avg_rating', '-created_at')[:5]  # Get top 5 rated places
    website_reviews = WebsiteReview.objects.filter(is_visible=True).order_by('-created_at')[:3]  # Get latest 3 reviews
    return render(request, 'wandercritic/index.html', {
        'places': places,
        'website_reviews': website_reviews
    })

def explore(request):
    places = Place.objects.all()
    search_query = request.GET.get('search', '')
    category = request.GET.get('category', '')
    tag = request.GET.get('tag', '')
    budget_range = request.GET.get('budget_range', '')
    
    if search_query:
        places = places.filter(name__icontains=search_query) | \
                places.filter(description__icontains=search_query) | \
                places.filter(location__icontains=search_query)
    
    if category:
        places = places.filter(categories__name=category)
    
    if tag:
        places = places.filter(tags__name=tag)
    
    if budget_range:
        ranges = {
            '0-10': (0, 10),
            '11-20': (11, 20),
            '21-50': (21, 50),
            '51-100': (51, 100),
            '101-200': (101, 200),
            '201+': (201, 999999)
        }
        if budget_range in ranges:
            min_val, max_val = ranges[budget_range]
            if budget_range == '201+':
                places = places.filter(budget__gte=min_val)
            else:
                places = places.filter(budget__range=(min_val, max_val))
    
    # Get all categories and tags for filters
    categories = PlaceCategory.objects.all()
    tags = Tag.objects.all()
    
    # Define budget ranges for the template
    budget_ranges = [
        ('0-10', '£0 - £10'),
        ('11-20', '£11 - £20'),
        ('21-50', '£21 - £50'),
        ('51-100', '£51 - £100'),
        ('101-200', '£101 - £200'),
        ('201+', '£201+')
    ]
    
    places = places.annotate(
        avg_rating=Avg('review__rating')
    ).order_by('-avg_rating', '-created_at').distinct()
    
    context = {
        'places': places,
        'categories': categories,
        'tags': tags,
        'search_query': search_query,
        'selected_category': category,
        'selected_tag': tag,
        'budget_ranges': budget_ranges,
        'selected_budget_range': budget_range
    }
    return render(request, 'wandercritic/explore.html', context)

def about(request):
    return render(request, 'wandercritic/about.html')

def contact(request):
    return render(request, 'wandercritic/contact.html')

@login_required
def become_agent(request):
    # If already a travel agent, redirect to place creation
    if request.user.is_travel_agent:
        messages.info(request, "You are already a travel agent!")
        return redirect('wandercritic:place_create')
    
    # Check for pending application
    pending_application = TravelAgentApplication.objects.filter(
        user=request.user,
        status='pending'
    ).first()
    
    if pending_application:
        return render(request, 'wandercritic/become_agent.html', {
            'pending_application': pending_application
        })
    
    if request.method == 'POST':
        form = TravelAgentApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(request, 
                "Your application has been submitted successfully! We'll review it soon.")
            return redirect('wandercritic:become_agent')
    else:
        form = TravelAgentApplicationForm()
    
    return render(request, 'wandercritic/become_agent.html', {'form': form})

@login_required
def manage_reports(request):
    # Get all reports submitted by the user
    reports = Report.objects.filter(reporter=request.user).order_by('-created_at')
    return render(request, 'wandercritic/manage_reports.html', {
        'reports': reports
    })

def about_us(request):
    return render(request, 'wandercritic/about.html')

def contact_us(request):
    return render(request, 'wandercritic/contact.html')

@login_required
def review_delete(request, slug, review_id):
    review = get_object_or_404(Review, id=review_id, place__slug=slug)
    
    # Check if user has permission to delete the review
    if not (request.user == review.user or request.user.is_superuser):
        return HttpResponseForbidden("You don't have permission to delete this review.")
    
    # Store place reference before deleting review
    place = review.place
    
    # Delete the review
    review.delete()
    
    # Update place rating
    place.update_rating()
    
    messages.success(request, 'Review deleted successfully.')
    return redirect('wandercritic:place_detail', slug=slug)

@login_required
def report_place(request, slug):
    place = get_object_or_404(Place, slug=slug)
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.place = place
            report.save()
            messages.success(request, "Your report has been submitted successfully.")
            return redirect('wandercritic:place_detail', slug=slug)
    else:
        form = ReportForm()
    
    return render(request, 'wandercritic/report.html', {
        'form': form,
        'place': place
    })


@login_required
def report_review(request, slug, review_id):
    place = get_object_or_404(Place, slug=slug)
    review = get_object_or_404(Review, id=review_id)

    if request.method == "POST":
        form = ReportReviewForm(request.POST, review=review)
        
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.place = place
            report.review = review
            report.save()

            messages.success(request, "Your report has been submitted successfully.")
            return redirect('wandercritic:place_detail', slug=slug)
    else:
        form = ReportReviewForm(review=review) 

    return render(request, 'wandercritic/report_review.html', {
        'place': place,
        'review': review,
        'form': form
    })


def policy(request, policy_type):
    template_name = f'wandercritic/policies/{policy_type}.html'
    return render(request, template_name)

def place_list(request):
    places = Place.objects.all().order_by('-created_at')
    return render(request, 'wandercritic/place_list.html', {'places': places})

def place_detail(request, slug):
    place = get_object_or_404(Place, slug=slug)
    images = place.images.all()
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(place=place, user=request.user).first()

    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and comment:
            review, created = Review.objects.update_or_create(
                place=place,
                user=request.user,
                defaults={
                    'rating': rating,
                    'comment': comment
                }
            )
            messages.success(request, 'Your review has been posted!')
            return redirect('wandercritic:place_detail', slug=slug)

    reviews = Review.objects.filter(place=place).select_related('user')
    return render(request, 'wandercritic/place_detail.html', {
        'place': place,
        'images': images,
        'user_review': user_review,
        'reviews': reviews,
        'rating_choices': Review.RATING_CHOICES,
    })

@login_required
def place_create(request):
    if not request.user.is_travel_agent:
        messages.error(request, "Only travel agents can create new places.")
        return redirect('wandercritic:explore')
        
    if request.method == 'POST':
        form = PlaceForm(request.POST, request.FILES)
        if form.is_valid():
            place = form.save(commit=False)
            place.created_by = request.user
            place.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Handle additional images
            images = request.FILES.getlist('additional_images')
            for image in images:
                PlaceImage.objects.create(place=place, image=image)
                
            messages.success(request, f"{place.name} has been created successfully!")
            return redirect('wandercritic:place_detail', slug=place.slug)
    else:
        form = PlaceForm()
    
    return render(request, 'wandercritic/place_form.html', {'form': form})

@login_required
def place_edit(request, slug):
    place = get_object_or_404(Place, slug=slug)
    
    # Check if user has permission to edit
    if not (request.user == place.created_by or request.user.is_superuser):
        messages.error(request, "You don't have permission to edit this place.")
        return redirect('wandercritic:place_detail', slug=slug)
    
    if request.method == 'POST':
        form = PlaceForm(request.POST, request.FILES, instance=place)
        if form.is_valid():
            form.save()
            messages.success(request, 'Place updated successfully!')
            return redirect('wandercritic:place_detail', slug=place.slug)
    else:
        form = PlaceForm(instance=place)
    
    return render(request, 'wandercritic/place_form.html', {
        'form': form,
        'place': place,
        'edit_mode': True
    })

@login_required
def my_places(request):
    User = get_user_model()
    agent_id = request.GET.get('agent')
    if agent_id:
        # If agent_id is provided, show that agent's places
        agent = get_object_or_404(User, id=agent_id)
        places = Place.objects.filter(created_by=agent).order_by('-created_at')
        context = {
            'places': places,
            'viewing_agent': agent
        }
    else:
        # Otherwise show the current user's places
        places = Place.objects.filter(created_by=request.user).order_by('-created_at')
        context = {
            'places': places
        }
    return render(request, 'wandercritic/my_places.html', context)

@login_required
def place_delete(request, slug):
    place = get_object_or_404(Place, slug=slug)
    
    # Check if user has permission to delete
    if not (request.user.is_superuser or (request.user.is_travel_agent and request.user == place.created_by)):
        messages.error(request, "You don't have permission to delete this place.")
        return redirect('wandercritic:place_detail', slug=slug)
    
    if request.method == 'POST':
        place.delete()
        messages.success(request, f"{place.name} has been deleted successfully.")
        if request.user.is_superuser:
            return redirect('wandercritic:explore')
        return redirect('wandercritic:my_places')
    
    return render(request, 'wandercritic/place_delete.html', {'place': place})

@user_passes_test(is_superuser)
def admin_applications(request):
    applications = TravelAgentApplication.objects.filter(status='pending')
    return render(request, 'wandercritic/admin/applications.html', {
        'applications': applications
    })

@user_passes_test(is_superuser)
def admin_application_action(request, application_id, action):
    application = get_object_or_404(TravelAgentApplication, id=application_id)
    
    if action == 'approve':
        application.approve()
        messages.success(request, f"Application by {application.full_name} has been approved.")
    elif action == 'reject':
        application.reject()
        messages.success(request, f"Application by {application.full_name} has been rejected.")
    
    return redirect('wandercritic:admin_applications')

@user_passes_test(is_superuser)
def admin_reports(request):
    reports = Report.objects.all().order_by('-created_at')
    paginator = Paginator(reports, 10)  # 10 cards
    page_number = request.GET.get('page')
    reports_page = paginator.get_page(page_number)

    return render(request, 'wandercritic/admin/reports.html', {
        'reports': reports_page,
        'page_obj': reports_page
    })


@user_passes_test(is_superuser)
def admin_report_action(request, report_id, action):
    report = get_object_or_404(Report, id=report_id)
    
    if report.place:
        place_name = report.place.name
    elif report.content_type == 'bug':
        place_name = f"Bug on {report.url}"
    else:
        place_name = "Unknown Report"
    if action == 'resolve':
        report.resolve(request.user)
        messages.success(request, f"Report on {place_name} has been resolved.")
    elif action == 'dismiss':
        report.dismiss(request.user)
        messages.success(request, f"Report on {place_name} has been dismissed.")
    
    return redirect('wandercritic:admin_reports')

@login_required
def edit_profile(request):
    if request.user.is_travel_agent:
        form_class = TravelAgentProfileForm
    else:
        form_class = UserProfileForm

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('wandercritic:edit_profile')
    else:
        form = form_class(instance=request.user)
    
    return render(request, 'wandercritic/profile/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            messages.success(request, 'Password changed successfully! Please log in again.')
            return redirect('account_login')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'wandercritic/profile/change_password.html', {'form': form})


@login_required
def add_website_review(request):
    # Check if user already has a review
    existing_review = WebsiteReview.objects.filter(user=request.user).first()
    if existing_review:
        messages.info(request, 'You have already submitted a review. You can update it below.')
        form = WebsiteReviewForm(instance=existing_review)
    else:
        form = WebsiteReviewForm()

    if request.method == 'POST':
        if existing_review:
            form = WebsiteReviewForm(request.POST, instance=existing_review)
        else:
            form = WebsiteReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.role = 'Travel Agent' if request.user.is_travel_agent else 'User'
            review.save()
            messages.success(request, 'Thank you for your review!')
            return redirect('wandercritic:index')
    
    return render(request, 'wandercritic/website_review_form.html', {'form': form})


@login_required
def delete_website_review(request, review_id):
    review = get_object_or_404(WebsiteReview, id=review_id)
    
    # Check if user has permission to delete the review
    if not (request.user == review.user or request.user.is_superuser):
        return HttpResponseForbidden("You don't have permission to delete this review.")
    
    review.delete()
    messages.success(request, 'Review deleted successfully.')
    return redirect('wandercritic:index')


@login_required

def report_bug(request):
    full_url = request.GET.get('url', '')

    parsed_url = urlparse(full_url)
    path_only = parsed_url.path 

    current_url = f"http://{request.get_host()}{path_only}"

    if request.method == 'POST':
        form = BugReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.url = current_url
            report.reporter = request.user
            report.save()
            return redirect('wandercritic:index')
    else:
        form = BugReportForm()

    return render(request, 'wandercritic/report_bug.html', {
        'form': form,
        'url': current_url
    })
