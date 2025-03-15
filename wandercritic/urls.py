from django.urls import path
from wandercritic import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'wandercritic' 

urlpatterns = [
    path('', views.index, name='index'),
    path('explore/', views.explore, name='explore'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('become-agent/', views.become_agent, name='become_agent'),
    path('policies/<str:policy_type>/', views.policy, name='policy'),
    
    # Place URLs
    path('places/', views.place_list, name='place_list'),
    path('places/create/', views.place_create, name='place_create'),
    path('places/<slug:slug>/', views.place_detail, name='place_detail'),
    path('places/<slug:slug>/edit/', views.place_edit, name='place_edit'),
    path('places/<slug:slug>/delete/', views.place_delete, name='place_delete'),
    path('places/<slug:slug>/report/', views.report_place, name='report_place'),
    path('my-places/', views.my_places, name='my_places'),
    path('places/<slug:slug>/reviews/<int:review_id>/delete/', views.review_delete, name='review_delete'),
    path('reports/', views.manage_reports, name='manage_reports'),
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),
    
    # Admin URLs
    path('manage/applications/', views.admin_applications, name='admin_applications'),
    path('manage/applications/<int:application_id>/<str:action>/', 
         views.admin_application_action, name='admin_application_action'),
    path('manage/reports/', views.admin_reports, name='admin_reports'),
    path('manage/reports/<int:report_id>/<str:action>/', 
         views.admin_report_action, name='admin_report_action'),
    
    # Website Review URLs
    path('review/', views.add_website_review, name='add_website_review'),
    path('review/<int:review_id>/delete/', views.delete_website_review, name='delete_website_review'),
    # report a review and bug URLs
    path('place/<slug:slug>/review/<int:review_id>/report/', views.report_review, name='report_review'),
    path('report_bug/', views.report_bug, name='report_bug'), 
    
    # Profile URLs
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

