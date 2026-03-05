from django.core.management.base import BaseCommand
from datetime import date, timedelta  # ✅ include timedelta
from jobcard.models import JobCard

class Command(BaseCommand):
    help = "Prepopulate Day and Night Shift JobCards for all lines"

    def handle(self, *args, **options):
        lines = ["FL001", "FL006", "FL007", "FL008", "FL010", "FL013"]  # your lines
        shifts = ["Day Shift", "Night Shift"]
        today = date.today()
        night_date = today - timedelta(days=1)  # Night shift jobs belong to previous day

        for line in lines:
            for shift in shifts:
                target_date = night_date if shift == "Night Shift" else today
                job, created = JobCard.objects.get_or_create(
                    line=line,
                    shift=shift,
                    date=target_date,
                    defaults={
                        "wo_number": 1000 + int(line[-3:]),  # example WO number
                        "product_code": "PCODE" + line[-3:],
                        "product_name": "Product " + line[-3:],
                        "target_quantity": 1000,
                        "operator_names": "",
                        "supervisor_names": ""
                    }
                )
                if created:
                    self.stdout.write(f"Created {shift} JobCard for {line} on {target_date}")

        self.stdout.write("All Day and Night Shift JobCards have been prepopulated!")