from django.contrib import admin
from .models import JobCard

@admin.register(JobCard)
class JobCardAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ('date', 'line', 'wo_number', 'product_name', 'target_quantity', 'total_output')
    
    # Filters on the sidebar
    list_filter = ('line', 'date', 'shift')
    
    # Searchable fields
    search_fields = ('wo_number', 'product_code', 'product_name', 'operator_names', 'supervisor_names')
    
    # Organize fields into sections in the admin form
    fieldsets = (
        ('Job Details', {
            'fields': ('date', 'line', 'wo_number', 'shift', 'product_code', 'product_name', 'target_quantity')
        }),
        ('Hourly Output', {
            'fields': ('hour1', 'hour2', 'hour3', 'hour4', 'hour5', 'hour6', 'hour7', 'hour8', 'hour9', 'hour10', 'hour11')
        }),
        ('Damages / Rejects', {
            'fields': ('jar', 'cap', 'front_label', 'back_label', 'carton', 'sleeve', 'sticker', 'tube', 'packets', 'roll_on_ball', 'jar_pump')
        }),
        ('Operators / Supervisors', {
            'fields': ('operator_names', 'supervisor_names', 'line_captain_signature', 'supervisor_signature')
        }),
    )
