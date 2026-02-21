from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import PROVINCES

QUALIFICATION_LEVELS = [
    ('grade_10', 'Grade 10'),
    ('grade_12', 'Grade 12'),
    ('certificate', 'Certificate'),
    ('diploma', 'Diploma'),
    ('degree', 'Bachelor\'s Degree'),
    ('postgraduate', 'Postgraduate'),
]

CATEGORIES = [
    ('correctional_officer', 'Correctional Officer'),
    ('health', 'Health & Medical'),
    ('administration', 'Administration'),
    ('finance', 'Finance & Accounts'),
    ('engineering', 'Engineering & Technical'),
    ('legal', 'Legal'),
    ('security', 'Security'),
    ('it', 'Information Technology'),
    ('education', 'Education & Training'),
    ('other', 'Other'),
]

VACANCY_STATUS = [
    ('draft', 'Draft'),
    ('open', 'Open'),
    ('closed', 'Closed'),
    ('cancelled', 'Cancelled'),
]

APPLICATION_STATUS = [
    ('submitted', 'Submitted'),
    ('under_review', 'Under Review'),
    ('shortlisted', 'Shortlisted'),
    ('interview_scheduled', 'Interview Scheduled'),
    ('interviewed', 'Interviewed'),
    ('selected', 'Selected'),
    ('rejected', 'Rejected'),
    ('withdrawn', 'Withdrawn'),
]

GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]


class Vacancy(models.Model):
    title = models.CharField(max_length=200)
    reference_number = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    province = models.CharField(max_length=50, choices=PROVINCES + [('All', 'All Provinces')])
    qualification_level = models.CharField(max_length=30, choices=QUALIFICATION_LEVELS)
    positions_available = models.PositiveIntegerField(default=1)
    description = models.TextField()
    requirements = models.TextField()
    min_age = models.PositiveIntegerField(default=18)
    max_age = models.PositiveIntegerField(default=45)
    salary_range = models.CharField(max_length=100, blank=True)
    open_date = models.DateField()
    close_date = models.DateField()
    status = models.CharField(max_length=20, choices=VACANCY_STATUS, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_vacancies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Vacancies'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_number} - {self.title}"

    def is_open(self):
        today = timezone.now().date()
        return self.status == 'open' and self.open_date <= today <= self.close_date

    def application_count(self):
        return self.applications.count()


class Application(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')

    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    province = models.CharField(max_length=50, choices=PROVINCES)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    nationality = models.CharField(max_length=50, default='Papua New Guinean')

    # Education
    highest_qualification = models.CharField(max_length=30, choices=QUALIFICATION_LEVELS)
    institution = models.CharField(max_length=200)
    year_completed = models.PositiveIntegerField()
    grade_result = models.CharField(max_length=100, help_text='e.g. GPA 3.5/4.0, Credit, Distinction')

    # Work Experience
    years_experience = models.PositiveIntegerField(default=0)
    current_employer = models.CharField(max_length=200, blank=True)
    current_position = models.CharField(max_length=200, blank=True)
    work_history = models.TextField(blank=True, help_text='Briefly describe your work history')

    # References
    reference1_name = models.CharField(max_length=100)
    reference1_position = models.CharField(max_length=100)
    reference1_phone = models.CharField(max_length=20)
    reference2_name = models.CharField(max_length=100, blank=True)
    reference2_position = models.CharField(max_length=100, blank=True)
    reference2_phone = models.CharField(max_length=20, blank=True)

    # Cover letter
    cover_letter = models.TextField(blank=True)

    # Status & Score
    status = models.CharField(max_length=30, choices=APPLICATION_STATUS, default='submitted')
    total_score = models.FloatField(null=True, blank=True)
    ai_summary = models.TextField(blank=True, help_text='AI-generated summary of application')

    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hr_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['vacancy', 'applicant']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.vacancy.title}"

    def get_age(self):
        from datetime import date
        today = date.today()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def compute_score(self):
        """Automated scoring: Education 30%, Grade 25%, Experience 20%, Province 10%, Completeness 15%"""
        score = 0.0

        # Education score (30%)
        edu_scores = {
            'grade_10': 10, 'grade_12': 20, 'certificate': 60,
            'diploma': 75, 'degree': 90, 'postgraduate': 100
        }
        edu_score = edu_scores.get(self.highest_qualification, 0)
        score += (edu_score / 100) * 30

        # Grade/result score (25%) - simple heuristic
        grade = self.grade_result.lower()
        if any(k in grade for k in ['distinction', 'high distinction', '4.0', 'a+']):
            grade_score = 100
        elif any(k in grade for k in ['credit', 'merit', '3.5', '3.7', 'b+']):
            grade_score = 80
        elif any(k in grade for k in ['pass', '3.0', 'b', 'c']):
            grade_score = 60
        elif any(k in grade for k in ['2.0', '2.5', 'd']):
            grade_score = 40
        else:
            grade_score = 50
        score += (grade_score / 100) * 25

        # Experience score (20%)
        years = min(self.years_experience, 10)
        exp_score = min(years * 10, 100)
        score += (exp_score / 100) * 20

        # Province match (10%) - prefer matching province
        if self.province == self.vacancy.province or self.vacancy.province == 'All':
            province_score = 100
        else:
            province_score = 60
        score += (province_score / 100) * 10

        # Completeness score (15%)
        fields = [self.work_history, self.cover_letter, self.current_employer,
                  self.reference2_name, self.reference2_phone]
        filled = sum(1 for f in fields if f.strip())
        completeness_score = (filled / len(fields)) * 100
        score += (completeness_score / 100) * 15

        self.total_score = round(score, 2)

        # Generate AI summary
        self.ai_summary = (
            f"Applicant {self.full_name()} from {self.province} applied for {self.vacancy.title}. "
            f"Highest qualification: {self.get_highest_qualification_display()} from {self.institution} ({self.year_completed}), "
            f"result: {self.grade_result}. "
            f"Work experience: {self.years_experience} year(s). "
            f"Automated score: {self.total_score}/100."
        )
        self.save(update_fields=['total_score', 'ai_summary'])
        return self.total_score


DOC_TYPES = [
    ('cv', 'Curriculum Vitae (CV)'),
    ('cover_letter', 'Cover Letter'),
    ('national_id', 'National ID / Passport'),
    ('birth_certificate', 'Birth Certificate'),
    ('academic_transcript', 'Academic Transcript / Results'),
    ('qualification', 'Qualification / Certificate'),
    ('reference_letter', 'Reference Letter'),
    ('other', 'Other'),
]


class Document(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=30, choices=DOC_TYPES)
    file = models.FileField(upload_to='documents/%Y/%m/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    ocr_text = models.TextField(blank=True, help_text='Extracted text from document (OCR)')
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_docs')
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_doc_type_display()} - {self.application.full_name()}"


class Interview(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    scheduled_date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    panel_members = models.ManyToManyField(User, related_name='interview_panels', blank=True)
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ], default='scheduled')
    notes = models.TextField(blank=True)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview: {self.application.full_name()} on {self.scheduled_date.date()}"

    def average_panel_score(self):
        scores = self.panel_scores.all()
        if scores:
            return round(sum(s.score for s in scores) / len(scores), 2)
        return None


class InterviewScore(models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='panel_scores')
    panel_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_scores')
    score = models.FloatField(help_text='Score out of 100')
    communication_score = models.FloatField(default=0, help_text='Communication skills (out of 20)')
    knowledge_score = models.FloatField(default=0, help_text='Job knowledge (out of 30)')
    attitude_score = models.FloatField(default=0, help_text='Attitude & professionalism (out of 25)')
    experience_score = models.FloatField(default=0, help_text='Relevant experience (out of 25)')
    comments = models.TextField(blank=True)
    recommendation = models.CharField(max_length=20, choices=[
        ('recommend', 'Recommend'),
        ('conditional', 'Conditional Recommend'),
        ('not_recommend', 'Do Not Recommend'),
    ], blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['interview', 'panel_member']

    def save(self, *args, **kwargs):
        self.score = self.communication_score + self.knowledge_score + self.attitude_score + self.experience_score
        super().save(*args, **kwargs)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=[
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('status_update', 'Status Update'),
        ('interview', 'Interview'),
    ], default='info')
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} -> {self.user.username}"


class BulkMessage(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    recipient_status = models.CharField(max_length=30, blank=True, help_text='Target application status filter')
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    recipient_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.subject} ({self.sent_at.date()})"
