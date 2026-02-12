from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.jobcard_create, name='jobcard_create'),
    path('success/', views.success, name='jobcard_success'),
]
