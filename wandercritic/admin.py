from django.contrib import admin
from .models import User, Place, PlaceImage, PlaceCategory, Tag, TravelAgentApplication, Report

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_travel_agent', 'is_staff')
    list_filter = ('is_travel_agent', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at', 'average_rating')
    list_filter = ('categories', 'created_at')
    search_fields = ('name', 'description', 'location')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(PlaceImage)
class PlaceImageAdmin(admin.ModelAdmin):
    list_display = ('place', 'caption', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('place__name', 'caption')

@admin.register(PlaceCategory)
class PlaceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(TravelAgentApplication)
class TravelAgentApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'user__username', 'company_name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'place', 'report_type', 'status', 'created_at')
    list_filter = ('status', 'report_type', 'created_at')
    search_fields = ('reporter__username', 'place__name', 'description')
    readonly_fields = ('created_at', 'resolved_at')