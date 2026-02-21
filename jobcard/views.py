from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from .forms import TempSubmissionForm, JobCardForm, JobCardPrepopulateForm
from .models import TempSubmission, ShiftSubmission, JobCard
from datetime import date


# -----------------------------
# LIVE OPERATOR ENTRY (UNCHANGED)
# -----------------------------
def temp_submission(request):
    today = timezone.localdate()
    user = request.user if request.user.is_authenticated else None
    shift = request.GET.get("shift", "Day")
# Get all lines from choices
    from .models import LINE_CHOICES
    lines = [l[0] for l in LINE_CHOICES]
    forms_data = []

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        line = request.POST.get("line")
        shift_post = request.POST.get("shift", shift)

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

            if new_val in [None, ""]:
                continue

            try:
                new_val = float(new_val)
            except:
                continue

            if old_val not in [None, 0, 0.0]:
                return JsonResponse({
                    "error": f"{field.upper()} already submitted and locked."
                }, status=403)

            if new_val == 0:
                continue

            setattr(obj, field, new_val)
            updated_fields.append(i)

        obj.save()
        return JsonResponse({"success": True, "updated": updated_fields})


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

    if request.GET.get("ajax") == "1":
        return JsonResponse({"global_locked_hours": global_locked_hours})

    dashboard_data = {}

    for sub in submissions:
        key = f"{sub.line}_{sub.shift}"

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

    return redirect("jobcard:supervisor_dashboard")


# -----------------------------
# JOBCARD FORM (FINAL OPERATOR ENTRY)
# -----------------------------
def jobcard_operator_entry(request):
    today = timezone.localdate()

    if request.method == "POST":
        line = request.POST.get("line")
        shift = request.POST.get("shift")

        jobcard = JobCard.objects.filter(date=today, line=line, shift=shift).first()

        if not jobcard:
            messages.error(request, "No JobCard created for this line/shift.")
            return redirect("jobcard:jobcard_create")

        # 🚫 BLOCK DUPLICATE SUBMISSION
        if jobcard.is_submitted:
            messages.error(request, "This JobCard was already submitted. Duplicate entries are not allowed.")
            return redirect(request.path + f"?line={line}&shift={shift}")

        form = JobCardForm(request.POST, instance=jobcard)

        if form.is_valid():
            obj = form.save(commit=False)

            # mark as submitted so nobody can submit again
            obj.is_submitted = True
            obj.save()

            messages.success(request, "✅ JobCard submitted successfully!")
            return redirect("jobcard:jobcard_success")
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        line = request.GET.get("line")
        shift = request.GET.get("shift")
        jobcard = JobCard.objects.filter(date=today, line=line, shift=shift).first()

        if jobcard:
            form = JobCardForm(instance=jobcard)
        else:
            form = JobCardForm()

    return render(request, "jobcard_form.html", {"form": form})


# -----------------------------
# SUCCESS PAGE
# -----------------------------
def jobcard_success(request):
    return render(request, "success.html")


# -----------------------------
# SUPERVISOR PREPOPULATE
# -----------------------------
def jobcard_prepopulate(request):
    today = timezone.localdate()

    if request.method == "POST":
        form = JobCardPrepopulateForm(request.POST)

        if form.is_valid():
            line = form.cleaned_data['line']
            shift = form.cleaned_data['shift']

            jobcard, created = JobCard.objects.get_or_create(
                date=today,
                line=line,
                shift=shift,
                defaults={
                    "wo_number": form.cleaned_data['wo_number'],
                    "product_code": form.cleaned_data['product_code'],
                    "product_name": form.cleaned_data['product_name'],
                    "target_quantity": form.cleaned_data['target_quantity'],
                    "operator_names": "",
                    "supervisor_names": "",
                }
            )

            if not created:
                jobcard.wo_number = form.cleaned_data['wo_number']
                jobcard.product_code = form.cleaned_data['product_code']
                jobcard.product_name = form.cleaned_data['product_name']
                jobcard.target_quantity = form.cleaned_data['target_quantity']
                jobcard.save()

                messages.success(request, f"JobCard for {line} ({shift}) updated.")
            else:
                messages.success(request, f"JobCard for {line} ({shift}) created.")

            return redirect('jobcard:jobcard_prepopulate')

    else:
        form = JobCardPrepopulateForm()

    return render(request, "jobcard_prepopulate.html", {"form": form})


# -----------------------------
# GET JOBCARD (AJAX LOAD)
# -----------------------------
def get_jobcard(request):
    line = request.GET.get("line")
    shift = request.GET.get("shift")

    try:
        job = JobCard.objects.get(
            line=line,
            shift=shift,
            date=date.today()
        )

        already_submitted = bool(job.operator_names or job.hour1)

        return JsonResponse({
            "wo_number": job.wo_number,
            "product_code": job.product_code,
            "product_name": job.product_name,
            "target_quantity": job.target_quantity,
            "operator_names": job.operator_names,
            "supervisor_names": job.supervisor_names,
            "submitted": already_submitted
        })

    except JobCard.DoesNotExist:
        return JsonResponse({"error": "No jobcard found for this line & shift"})