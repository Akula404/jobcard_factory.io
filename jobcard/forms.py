from django import forms
from .models import JobCard, TempSubmission

class JobCardForm(forms.ModelForm):
    class Meta:
        model = JobCard
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'operator_names': forms.Textarea(attrs={'rows': 3}),
            'supervisor_names': forms.Textarea(attrs={'rows': 3}),
        }

class TempSubmissionForm(forms.ModelForm):
    class Meta:
        model = TempSubmission
        fields = [
            "hour1","hour2","hour3","hour4","hour5",
            "hour6","hour7","hour8","hour9","hour10","hour11"
        ]
