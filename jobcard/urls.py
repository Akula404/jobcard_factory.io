from django.urls import path
from . import views

app_name = "jobcard"  # important for namespacing in redirects

urlpatterns = [
    # JobCard
    path('new/', views.jobcard_create, name='jobcard_create'),
    path('success/', views.jobcard_success, name='jobcard_success'),

    # Operator realtime submissions
    path('temp-submission/', views.temp_submission, name='temp_submission'),

    # Supervisor dashboard
    path('supervisor-dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),

    # Finalize shift
    path('finalize-shift/<str:line>/<str:shift>/', views.finalize_shift, name='finalize_shift'),
]
