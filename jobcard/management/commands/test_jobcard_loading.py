from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from jobcard.models import JobCard, TempSubmission

class Command(BaseCommand):
    help = "Test if JobCards load correctly for Day and Night shifts"

    def handle(self, *args, **options):
        lines = JobCard.objects.values_list('line', flat=True).distinct()
        now = timezone.localtime()
        today = now.date()

        for line in lines:
            for shift in ["Day Shift", "Night Shift"]:
                # Determine target_date for Night Shift
                target_date = today
                if shift == "Night Shift" and (now.hour < 5 or (now.hour == 5 and now.minute < 30)):
                    target_date = today - timedelta(days=1)

                try:
                    job = JobCard.objects.get(line=line, shift=shift, date=target_date)
                    temp = TempSubmission.objects.filter(date=target_date, line=line, shift=shift).first()
                    hours = [0]*11
                    if temp:
                        hours = [getattr(temp, f"hour{i}", 0) or 0 for i in range(1, 12)]

                    self.stdout.write(f"✅ Loaded {line} | {shift} | {target_date} | WO: {job.wo_number}")

                except JobCard.DoesNotExist:
                    self.stdout.write(f"❌ Missing JobCard for {line} | {shift} | {target_date}")

        self.stdout.write("All JobCards have been tested!")