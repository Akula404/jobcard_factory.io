from django.urls import path
from . import views

app_name = 'jobcard'

urlpatterns = [
    # Operator JobCard Entry
    path('operator/', views.jobcard_operator_entry, name='operator_entry'),

    # Success page
    path('success/', views.jobcard_success, name='jobcard_success'),

    # Optional: page to create new JobCard if missing
    path('create/', views.jobcard_operator_entry, name='jobcard_create'),

    # Temp Submissions
    path('temp-submission/', views.temp_submission, name='temp_submission'),

    # Supervisor dashboard
    path('supervisor-dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),

    # Finalize shift
    path('finalize-shift/<str:line>/<str:shift>/', views.finalize_shift, name='finalize_shift'),

    # Prepopulate JobCards
    path('prepopulate/', views.jobcard_prepopulate, name='jobcard_prepopulate'),

    # AJAX endpoint to fetch JobCard details
    path("get-jobcard/", views.get_jobcard, name="get_jobcard"),

    # CSV export
    path('export-jobcards-csv/', views.export_jobcards_csv, name='export_jobcards_csv'),

    # Reset shift button
    path('reset-shift/', views.reset_shift, name='reset_shift'),


]