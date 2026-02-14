from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.postgres.fields import JSONField 

# -----------------------------
# CHOICES
# -----------------------------
LINE_CHOICES = [
    ('line1', 'Line 1'),
    ('line2', 'Line 2'),
    ('line3', 'Line 3'),
    ('line4', 'Line 4'),
    ('line5', 'Line 5'),
    ('line6', 'Line 6'),
    ('line7', 'Line 7'),
]

SHIFT_CHOICES = [
    ('Day', 'Day Shift'),
    ('Night', 'Night Shift'),
]

# =====================================================
# FINAL JOBCARD (Saved only after supervisor confirms)
# =====================================================
class JobCard(models.Model):
    date = models.DateField(default=timezone.localdate)
    line = models.CharField(max_length=10, choices=LINE_CHOICES)
    wo_number = models.CharField(max_length=50)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    product_code = models.CharField(max_length=50)
    product_name = models.CharField(max_length=100)
    target_quantity = models.PositiveIntegerField(default=0)

    hour1 = models.PositiveIntegerField(default=0)
    hour2 = models.PositiveIntegerField(default=0)
    hour3 = models.PositiveIntegerField(default=0)
    hour4 = models.PositiveIntegerField(default=0)
    hour5 = models.PositiveIntegerField(default=0)
    hour6 = models.PositiveIntegerField(default=0)
    hour7 = models.PositiveIntegerField(default=0)
    hour8 = models.PositiveIntegerField(default=0)
    hour9 = models.PositiveIntegerField(default=0)
    hour10 = models.PositiveIntegerField(default=0)
    hour11 = models.PositiveIntegerField(default=0)

    jar = models.PositiveIntegerField(default=0)
    cap = models.PositiveIntegerField(default=0)
    front_label = models.PositiveIntegerField(default=0)
    back_label = models.PositiveIntegerField(default=0)
    carton = models.PositiveIntegerField(default=0)
    sleeve = models.PositiveIntegerField(default=0)
    sticker = models.PositiveIntegerField(default=0)
    tube = models.PositiveIntegerField(default=0)
    packets = models.PositiveIntegerField(default=0)
    roll_on_ball = models.PositiveIntegerField(default=0)
    jar_pump = models.PositiveIntegerField(default=0)

    operator_names = models.TextField()
    supervisor_names = models.TextField()
    line_captain_signature = models.CharField(max_length=100)
    supervisor_signature = models.CharField(max_length=100)

    def total_output(self):
        return sum([
            self.hour1, self.hour2, self.hour3, self.hour4, self.hour5,
            self.hour6, self.hour7, self.hour8, self.hour9, self.hour10,
            self.hour11
        ])

    def __str__(self):
        return f"{self.date} | {self.product_name} | {self.line} | {self.shift}"


# =====================================================
# LIVE OPERATOR ENTRY TABLE (REALTIME DATA)
# =====================================================
class TempSubmission(models.Model):
    operator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    line = models.CharField(max_length=10, choices=LINE_CHOICES)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    date = models.DateField(default=timezone.localdate)

    hour1 = models.PositiveIntegerField(default=0)
    hour2 = models.PositiveIntegerField(default=0)
    hour3 = models.PositiveIntegerField(default=0)
    hour4 = models.PositiveIntegerField(default=0)
    hour5 = models.PositiveIntegerField(default=0)
    hour6 = models.PositiveIntegerField(default=0)
    hour7 = models.PositiveIntegerField(default=0)
    hour8 = models.PositiveIntegerField(default=0)
    hour9 = models.PositiveIntegerField(default=0)
    hour10 = models.PositiveIntegerField(default=0)
    hour11 = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    def total_output(self):
        return sum([
            self.hour1, self.hour2, self.hour3, self.hour4, self.hour5,
            self.hour6, self.hour7, self.hour8, self.hour9, self.hour10,
            self.hour11
        ])

    def __str__(self):
        name = self.operator.username if self.operator else "Anonymous"
        return f"{name} | {self.date} | {self.shift} | {self.line}"


# =====================================================
# SHIFT FINAL AGGREGATION TABLE
# =====================================================
class ShiftSubmission(models.Model):
    date = models.DateField()
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    line = models.CharField(max_length=10, choices=LINE_CHOICES)
    aggregated_data = models.JSONField(default=list)
    supervisor_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.date} - {self.shift} - {self.line}"
