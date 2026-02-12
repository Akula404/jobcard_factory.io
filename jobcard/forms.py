from django import forms
from .models import JobCard

class JobCardForm(forms.ModelForm):
    class Meta:
        model = JobCard
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'line': forms.Select(),
            'operator_names': forms.Textarea(attrs={'rows': 3}),
            'supervisor_names': forms.Textarea(attrs={'rows': 3}),
        }
