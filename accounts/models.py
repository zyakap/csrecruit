from django.db import models
from django.contrib.auth.models import User

ROLE_APPLICANT = 'applicant'
ROLE_HR_ADMIN = 'hr_admin'
ROLE_PANEL = 'panel_member'
ROLE_CHOICES = [
    (ROLE_APPLICANT, 'Applicant'),
    (ROLE_HR_ADMIN, 'HR Administrator'),
    (ROLE_PANEL, 'Panel Member'),
]

PROVINCES = [
    ('Central', 'Central'),
    ('Chimbu', 'Chimbu'),
    ('Eastern Highlands', 'Eastern Highlands'),
    ('East New Britain', 'East New Britain'),
    ('East Sepik', 'East Sepik'),
    ('Enga', 'Enga'),
    ('Gulf', 'Gulf'),
    ('Hela', 'Hela'),
    ('Jiwaka', 'Jiwaka'),
    ('Madang', 'Madang'),
    ('Manus', 'Manus'),
    ('Milne Bay', 'Milne Bay'),
    ('Morobe', 'Morobe'),
    ('New Ireland', 'New Ireland'),
    ('NCD (Port Moresby)', 'NCD (Port Moresby)'),
    ('Oro (Northern)', 'Oro (Northern)'),
    ('Sandaun (West Sepik)', 'Sandaun (West Sepik)'),
    ('Southern Highlands', 'Southern Highlands'),
    ('Western', 'Western'),
    ('Western Highlands', 'Western Highlands'),
    ('West New Britain', 'West New Britain'),
    ('Bougainville', 'Bougainville'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_APPLICANT)
    phone = models.CharField(max_length=20, blank=True)
    province = models.CharField(max_length=50, choices=PROVINCES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True)
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"

    def is_hr_admin(self):
        return self.role == ROLE_HR_ADMIN

    def is_panel_member(self):
        return self.role == ROLE_PANEL

    def is_applicant(self):
        return self.role == ROLE_APPLICANT
