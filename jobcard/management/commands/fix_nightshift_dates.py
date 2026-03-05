from django.core.management.base import BaseCommand
from datetime import timedelta
from jobcard.models import JobCard

class Command(BaseCommand):
    help = "Adjust Night Shift jobcard dates to previous day"

    def handle(self, *args, **options):
        night_jobs = JobCard.objects.filter(shift__iexact="Night")
        for job in night_jobs:
            old_date = job.date
            job.date = old_date - timedelta(days=1)
            job.save()
            self.stdout.write(f"Updated {job.line} from {old_date} to {job.date}")
        self.stdout.write(self.style.SUCCESS("All Night Shift dates have been fixed!"))