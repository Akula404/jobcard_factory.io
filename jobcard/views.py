from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import JsonResponse
from .forms import TempSubmissionForm, JobCardForm
from .models import TempSubmission, ShiftSubmission, JobCard

# -----------------------------
# LIVE OPERATOR ENTRY
# -----------------------------
def temp_submission(request):
    today = timezone.localdate()
    user = request.user if request.user.is_authenticated else None
    shift = request.GET.get("shift", "Day")

    # ---------- AJAX SAVE ----------
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        line = request.POST.get("line")
        if not line:
            return JsonResponse({"error": "Line not specified"}, status=400)

        obj, _ = TempSubmission.objects.get_or_create(
            operator=user,
            date=today,
            shift=shift,
            line=line
        )

        form = TempSubmissionForm(request.POST, instance=obj)
        if form.is_valid():
            saved = form.save()
            return JsonResponse({"total": saved.total_output()})
        return JsonResponse({"error": "Invalid data"}, status=400)

    # ---------- PAGE LOAD ----------
    lines = ["line1","line2","line3","line4","line5","line6","line7"]
    forms_data = []
    for line in lines:
        obj, _ = TempSubmission.objects.get_or_create(
            operator=user,
            date=today,
            shift=shift,
            line=line
        )
        form = TempSubmissionForm(instance=obj)
        forms_data.append((line, form, obj))

    return render(request, "temp_submission_form.html", {
        "forms_data": forms_data,
        "shift": shift
    })


# -----------------------------
# SUPERVISOR DASHBOARD (LIVE)
# -----------------------------
def supervisor_dashboard(request):
    today = timezone.localdate()
    lines = ["line1","line2","line3","line4","line5","line6","line7"]
    shifts = ["Day","Night"]

    submissions = TempSubmission.objects.filter(date=today)
    dashboard_data = {}

    for line in lines:
        for shift in shifts:
            key = f"{line}_{shift}"
            line_subs = submissions.filter(line=line, shift=shift)

            hour_totals = [0]*11
            total = 0

            for sub in line_subs:
                hours = [
                    sub.hour1, sub.hour2, sub.hour3, sub.hour4, sub.hour5,
                    sub.hour6, sub.hour7, sub.hour8, sub.hour9, sub.hour10, sub.hour11
                ]
                for i in range(11):
                    hour_totals[i] += hours[i] or 0
                total += sub.total_output()

            dashboard_data[key] = {
                "submissions": line_subs,
                "hour_totals": hour_totals,
                "total": total
            }

    return render(request,"supervisor_dashboard.html",{
        "dashboard_data": dashboard_data,
        "today": today,
        "hour_range": range(1,12)
    })


# -----------------------------
# FINALIZE SHIFT
# -----------------------------
def finalize_shift(request, line, shift):
    today = timezone.localdate()
    submissions = TempSubmission.objects.filter(date=today, line=line, shift=shift)

    aggregated_data = []
    for s in submissions:
        aggregated_data.append({
            "operator": s.operator.username if s.operator else "Anonymous",
            "hours": [
                s.hour1, s.hour2, s.hour3, s.hour4, s.hour5,
                s.hour6, s.hour7, s.hour8, s.hour9, s.hour10, s.hour11
            ],
            "total": s.total_output()
        })

    shift_submission, created = ShiftSubmission.objects.get_or_create(
        date=today,
        line=line,
        shift=shift,
        defaults={"aggregated_data": aggregated_data}
    )

    if not created:
        shift_submission.aggregated_data = aggregated_data
        shift_submission.save()

    return redirect("supervisor_dashboard")


# -----------------------------
# JOBCARD FORM
# -----------------------------
def jobcard_create(request):
    if request.method == "POST":
        form = JobCardForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('jobcard:jobcard_success')
    else:
        form = JobCardForm()
    return render(request, "jobcard_form.html", {"form": form, "hour_range": range(1,12)})


def jobcard_success(request):
    return render(request, "success.html")
