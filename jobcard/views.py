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
    shift = request.GET.get("shift", "Day")  # Day or Night

    lines = ["line1","line2","line3","line4","line5","line6","line7"]
    forms_data = []

    # ---------- AJAX SAVE ----------
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":

        line = request.POST.get("line")
        shift_post = request.POST.get("shift", shift)

        # get or create for correct shift
        obj, _ = TempSubmission.objects.get_or_create(
            operator=user,
            date=today,
            shift=shift_post,
            line=line
        )

        updated_fields = []

        for i in range(1, 12):
            field = f"hour{i}"
            new_val = request.POST.get(field)
            old_val = getattr(obj, field)

            # skip empty input
            if new_val in [None, ""]:
                continue

            try:
                new_val = float(new_val)
            except:
                continue

            # LOCK RULE: only overwrite if old value is None or 0
            if old_val not in [None, 0, 0.0]:
                return JsonResponse({
                    "error": f"{field.upper()} already submitted and locked."
                }, status=403)

            # do not save zero values
            if new_val == 0:
                continue

            setattr(obj, field, new_val)
            updated_fields.append(i)

        obj.save()

        return JsonResponse({
            "success": True,
            "updated": updated_fields
        })

    # ---------- PAGE LOAD ----------
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
# SUPERVISOR DASHBOARD
# -----------------------------
def supervisor_dashboard(request):
    today = timezone.localdate()
    submissions = TempSubmission.objects.filter(date=today).order_by('line', 'shift', 'operator')

    lines = ["line1","line2","line3","line4","line5","line6","line7"]

    global_locked_hours = []
    for h in range(1, 12):
        filled_lines = (
            submissions
            .exclude(**{f"hour{h}__isnull": True})
            .exclude(**{f"hour{h}": 0})
            .values("line")
            .distinct()
            .count()
        )
        if filled_lines >= len(lines):
            global_locked_hours.append(h)

    # AJAX polling
    if request.GET.get("ajax") == "1":
        return JsonResponse({"global_locked_hours": global_locked_hours})

    # Prepare dashboard data: separate Day/Night shift
    dashboard_data = {}
    for sub in submissions:
        key = f"{sub.line}_{sub.shift}"  # e.g., "line1_Day", "line1_Night"

        if key not in dashboard_data:
            dashboard_data[key] = {
                "submissions": [],
                "hour_totals": [0]*11,
                "total": 0
            }

        dashboard_data[key]["submissions"].append(sub)

        hours = [
            sub.hour1, sub.hour2, sub.hour3, sub.hour4, sub.hour5,
            sub.hour6, sub.hour7, sub.hour8, sub.hour9, sub.hour10, sub.hour11
        ]

        for i in range(11):
            dashboard_data[key]["hour_totals"][i] += hours[i] or 0

        dashboard_data[key]["total"] += sub.total_output()

    return render(request, "supervisor_dashboard.html", {
        "dashboard_data": dashboard_data,
        "today": today,
        "hour_range": range(1, 12)
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

    return render(request, "jobcard_form.html", {
        "form": form,
        "hour_range": range(1, 12)
    })


def jobcard_success(request):
    return render(request, "success.html")
