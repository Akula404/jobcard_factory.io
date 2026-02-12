from django.shortcuts import render, redirect
from .forms import JobCardForm

def jobcard_create(request):
    if request.method == "POST":
        form = JobCardForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('jobcard_success')
    else:
        form = JobCardForm()

    return render(request, "jobcard_form.html", {"form": form})

def success(request):
    return render(request, "success.html")
