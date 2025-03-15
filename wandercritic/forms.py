from typing import Any
from django import forms
from .models import User
from .models import Place, PlaceImage, TravelAgentApplication, Report, WebsiteReview
import json

from allauth.account.forms import LoginForm
class MyCustomLoginForm(LoginForm):

    def login(self, *args, **kwargs):

        # Add your own processing here.
        # You must return the original result.
        return super(MyCustomLoginForm, self).login(*args, **kwargs)
    

from allauth.account.forms import SignupForm
class MyCustomSignupForm(SignupForm):

    def save(self, request):

        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(MyCustomSignupForm, self).save(request)

        # Add your own processing here.
        # You must return the original result.
        return user

class PlaceForm(forms.ModelForm):
    highlights = forms.CharField(widget=forms.Textarea, required=False,
                               help_text="Enter each highlight on a new line")
    tips = forms.CharField(widget=forms.Textarea, required=False,
                         help_text="Enter each tip on a new line")
    
    class Meta:
        model = Place
        fields = ['name', 'description', 'short_description', 'location', 
                 'image', 'history', 'highlights', 'best_time_to_visit',
                 'getting_there', 'tips', 'categories', 'tags', 'budget']
    
    def clean_highlights(self):
        highlights = self.cleaned_data.get('highlights', '')
        if highlights:
            # Convert newline-separated text to JSON list
            highlights_list = [h.strip() for h in highlights.split('\n') if h.strip()]
            return json.dumps(highlights_list)
        return ''
    
    def clean_tips(self):
        tips = self.cleaned_data.get('tips', '')
        if tips:
            # Convert newline-separated text to JSON list
            tips_list = [t.strip() for t in tips.split('\n') if t.strip()]
            return json.dumps(tips_list)
        return ''

class PlaceImageForm(forms.ModelForm):
    class Meta:
        model = PlaceImage
        fields = ['image', 'caption', 'is_primary']

class TravelAgentApplicationForm(forms.ModelForm):
    class Meta:
        model = TravelAgentApplication
        fields = ['full_name', 'company_name', 'experience', 'website', 'phone']
        widgets = {
            'experience': forms.Textarea(attrs={'rows': 5}),
            'website': forms.URLInput(attrs={'placeholder': 'https://'}),
            'phone': forms.TextInput(attrs={'placeholder': '+1234567890'})
        }
        help_texts = {
            'experience': 'Tell us about your experience in the travel industry and why you want to become a travel agent.',
            'company_name': 'If you represent a company, enter its name here.',
            'website': 'Your personal or company website (optional)',
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['report_type', 'content_type', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Please provide details about your report...'}),
        }


class ReportReviewForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['report_type', 'description'] 

    def __init__(self, *args, **kwargs):
        self.review = kwargs.pop('review', None) 
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        report = super().save(commit=False)
        if self.review:
            report.content_type = 'review'
            report.review = self.review
        if commit:
            report.save()
        return report


class WebsiteReviewForm(forms.ModelForm):
    class Meta:
        model = WebsiteReview
        fields = ['rating', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience with WanderCritic...'}),
        }


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'contact_number', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
        }


class TravelAgentProfileForm(UserProfileForm):
    class Meta(UserProfileForm.Meta):
        fields = UserProfileForm.Meta.fields + ['company_name', 'company_website']


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Current password is incorrect')
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('New passwords do not match')
        return cleaned_data
    

class BugReportForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ['report_type', 'content_type', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Please provide details about your report...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the content_type as 'bug' by default
        self.fields['content_type'].initial = 'bug'
        self.fields['content_type'].disabled = True