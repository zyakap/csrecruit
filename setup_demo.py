#!/usr/bin/env python
"""
PNGCS Recruitment Portal — Demo Setup Script
Run with: python setup_demo.py
Creates demo users, vacancies, and applications for demonstration.
"""
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pngcs.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile, ROLE_HR_ADMIN, ROLE_PANEL, ROLE_APPLICANT
from recruitment.models import Vacancy, Application, Notification

DEMO_PASSWORD = 'demo1234'

print("=" * 60)
print("  PNGCS RECRUITMENT PORTAL — DEMO SETUP")
print("=" * 60)

# ── 1. HR Admin ───────────────────────────────────────────────
if not User.objects.filter(username='hradmin').exists():
    hr = User.objects.create_user('hradmin', 'hr@pngcs.gov.pg', DEMO_PASSWORD,
                                   first_name='Sarah', last_name='Kone')
    hr.is_staff = True
    hr.save()
    UserProfile.objects.create(user=hr, role=ROLE_HR_ADMIN, province='NCD (Port Moresby)')
    print("✓ HR Admin created: hradmin / demo1234")
else:
    hr = User.objects.get(username='hradmin')
    print("✓ HR Admin already exists")

# ── 2. Panel Members ──────────────────────────────────────────
panel_data = [
    ('panelist1', 'James', 'Opa', 'james.opa@pngcs.gov.pg', 'NCD (Port Moresby)'),
    ('panelist2', 'Mary', 'Tura', 'mary.tura@pngcs.gov.pg', 'Morobe'),
]
panel_users = []
for uname, fn, ln, email, prov in panel_data:
    if not User.objects.filter(username=uname).exists():
        u = User.objects.create_user(uname, email, DEMO_PASSWORD, first_name=fn, last_name=ln)
        UserProfile.objects.create(user=u, role=ROLE_PANEL, province=prov)
        print(f"✓ Panel Member: {uname} / demo1234")
    else:
        u = User.objects.get(username=uname)
        print(f"✓ Panel Member already exists: {uname}")
    panel_users.append(u)

# ── 3. Applicants ─────────────────────────────────────────────
applicant_data = [
    ('john.doe', 'John', 'Doe', 'john.doe@email.com', 'NCD (Port Moresby)', 'Male', '1995-04-12'),
    ('jane.smith', 'Jane', 'Smith', 'jane.smith@email.com', 'Morobe', 'Female', '1997-08-22'),
    ('peter.kila', 'Peter', 'Kila', 'peter.kila@email.com', 'Eastern Highlands', 'Male', '1993-01-15'),
    ('mary.toua', 'Mary', 'Toua', 'mary.toua@email.com', 'Western Highlands', 'Female', '1999-06-30'),
    ('paul.eto', 'Paul', 'Eto', 'paul.eto@email.com', 'Madang', 'Male', '1994-11-05'),
    ('grace.buri', 'Grace', 'Buri', 'grace.buri@email.com', 'East Sepik', 'Female', '1998-03-18'),
    ('david.ume', 'David', 'Ume', 'david.ume@email.com', 'Gulf', 'Male', '1992-09-25'),
    ('ruth.kapi', 'Ruth', 'Kapi', 'ruth.kapi@email.com', 'Bougainville', 'Female', '1996-12-08'),
]
applicants = []
for uname, fn, ln, email, prov, gender, dob in applicant_data:
    if not User.objects.filter(username=uname).exists():
        from datetime import date as d
        u = User.objects.create_user(uname, email, DEMO_PASSWORD, first_name=fn, last_name=ln)
        dob_date = d(*map(int, dob.split('-')))
        UserProfile.objects.create(
            user=u, role=ROLE_APPLICANT, province=prov, gender=gender, date_of_birth=dob_date
        )
        print(f"✓ Applicant: {uname} / demo1234")
    else:
        u = User.objects.get(username=uname)
        print(f"✓ Applicant already exists: {uname}")
    applicants.append(u)

# ── 4. Vacancies ──────────────────────────────────────────────
today = date.today()
vacancy_data = [
    {
        'title': 'Correctional Officer Grade 1',
        'reference_number': 'PNGCS-2026-CO-001',
        'department': 'Corrections Operations Division',
        'category': 'correctional_officer',
        'province': 'All',
        'qualification_level': 'grade_12',
        'positions_available': 150,
        'description': 'Correctional Officers are responsible for the safe and secure management of inmates at PNGCS facilities. '
                       'You will maintain order, enforce regulations, conduct searches, and support rehabilitation programs. '
                       'This is an exciting opportunity to serve Papua New Guinea and build a career in corrections.',
        'requirements': '- Minimum Grade 12 certificate or equivalent\n'
                        '- PNG citizen aged 18-35 years\n'
                        '- Physically fit and medically cleared\n'
                        '- Clean criminal record\n'
                        '- Good communication skills in English and Tok Pisin\n'
                        '- Willingness to work shifts including nights and weekends',
        'min_age': 18, 'max_age': 35,
        'salary_range': 'PGK 15,000 - 22,000 per annum',
        'open_date': today - timedelta(days=5),
        'close_date': today + timedelta(days=25),
        'status': 'open',
    },
    {
        'title': 'Senior Correctional Officer',
        'reference_number': 'PNGCS-2026-SCO-002',
        'department': 'Corrections Operations Division',
        'category': 'correctional_officer',
        'province': 'NCD (Port Moresby)',
        'qualification_level': 'diploma',
        'positions_available': 20,
        'description': 'Senior Correctional Officers provide leadership and supervision to junior officers, '
                       'manage inmate welfare programs, coordinate rehabilitation activities, and liaise with '
                       'welfare agencies and families. Preference given to current PNGCS employees.',
        'requirements': '- Diploma in Criminology, Law, Social Work, or related field\n'
                        '- Minimum 3 years correctional or related security experience\n'
                        '- PNG citizen aged 25-45 years\n'
                        '- Strong leadership and communication skills\n'
                        '- Clean disciplinary record',
        'min_age': 25, 'max_age': 45,
        'salary_range': 'PGK 28,000 - 38,000 per annum',
        'open_date': today - timedelta(days=3),
        'close_date': today + timedelta(days=20),
        'status': 'open',
    },
    {
        'title': 'Health Officer (Nurse)',
        'reference_number': 'PNGCS-2026-HO-003',
        'department': 'Health Services Division',
        'category': 'health',
        'province': 'All',
        'qualification_level': 'diploma',
        'positions_available': 30,
        'description': 'Health Officers provide primary healthcare services to inmates and staff at PNGCS facilities. '
                       'Responsibilities include conducting health assessments, administering medications, managing '
                       'chronic diseases, and implementing health promotion programs in correctional facilities.',
        'requirements': '- Diploma or Degree in Nursing from recognized PNG institution\n'
                        '- Registered with PNG Nursing Council\n'
                        '- Experience in community or clinical nursing preferred\n'
                        '- PNG citizen aged 21-45 years\n'
                        '- Valid practicing certificate',
        'min_age': 21, 'max_age': 45,
        'salary_range': 'PGK 22,000 - 32,000 per annum',
        'open_date': today - timedelta(days=2),
        'close_date': today + timedelta(days=18),
        'status': 'open',
    },
    {
        'title': 'Finance Officer',
        'reference_number': 'PNGCS-2026-FO-004',
        'department': 'Finance & Administration Division',
        'category': 'finance',
        'province': 'NCD (Port Moresby)',
        'qualification_level': 'degree',
        'positions_available': 5,
        'description': 'Finance Officers manage financial records, process payments, prepare financial reports, '
                       'assist with budget preparation, and ensure compliance with PFMA and government financial regulations.',
        'requirements': '- Bachelor\'s Degree in Accounting, Finance, or Commerce\n'
                        '- CPA PNG membership preferred\n'
                        '- Minimum 2 years government financial management experience\n'
                        '- Proficiency in MYOB, Quickbooks, or government financial systems\n'
                        '- PNG citizen aged 22-40 years',
        'min_age': 22, 'max_age': 40,
        'salary_range': 'PGK 35,000 - 50,000 per annum',
        'open_date': today - timedelta(days=1),
        'close_date': today + timedelta(days=14),
        'status': 'open',
    },
]

vacancies = []
for vdata in vacancy_data:
    vdata_copy = dict(vdata)
    ref = vdata_copy.pop('reference_number')
    if not Vacancy.objects.filter(reference_number=ref).exists():
        v = Vacancy.objects.create(reference_number=ref, created_by=hr, **vdata_copy)
        print(f"✓ Vacancy created: {ref} — {v.title}")
    else:
        v = Vacancy.objects.get(reference_number=ref)
        print(f"✓ Vacancy already exists: {ref}")
    vacancies.append(v)

# ── 5. Demo Applications ──────────────────────────────────────
app_data = [
    # (vacancy_idx, applicant_idx, qualification, institution, year, grade, experience, status)
    (0, 0, 'grade_12', 'Port Moresby Secondary School', 2015, 'Credit - 6 subjects passed', 3, 'under_review'),
    (0, 1, 'diploma', 'Pacific Adventist University', 2018, 'Distinction - GPA 3.8/4.0', 5, 'shortlisted'),
    (0, 2, 'certificate', 'UNITECH Lae', 2017, 'Pass - Certificate III', 4, 'shortlisted'),
    (0, 3, 'grade_12', 'Hagen Secondary School', 2016, 'Merit - B average', 2, 'submitted'),
    (0, 4, 'diploma', 'Divine Word University', 2019, 'Credit', 3, 'under_review'),
    (1, 1, 'diploma', 'Pacific Adventist University', 2018, 'Distinction - GPA 3.8/4.0', 5, 'interview_scheduled'),
    (2, 5, 'diploma', 'University of PNG School of Medicine', 2020, 'Distinction', 4, 'shortlisted'),
    (2, 6, 'degree', 'UPNG School of Medicine', 2019, 'GPA 3.2/4.0', 5, 'under_review'),
    (3, 7, 'degree', 'Divine Word University', 2021, 'Distinction - GPA 3.9/4.0', 2, 'submitted'),
]

print("\nCreating demo applications...")
for vacancy_idx, applicant_idx, qual, inst, year, grade, exp, status in app_data:
    vacancy = vacancies[vacancy_idx]
    applicant = applicants[applicant_idx]

    if Application.objects.filter(vacancy=vacancy, applicant=applicant).exists():
        print(f"  ✓ Application already exists: {applicant.get_full_name()} → {vacancy.reference_number}")
        continue

    app = Application.objects.create(
        vacancy=vacancy,
        applicant=applicant,
        first_name=applicant.first_name,
        last_name=applicant.last_name,
        date_of_birth=applicant.profile.date_of_birth or date(1995, 1, 1),
        gender=applicant.profile.gender or 'Male',
        province=applicant.profile.province,
        address=f'Section 7, Lot 12, {applicant.profile.province}, PNG',
        phone=f'+675 7{applicant.pk:03d} {applicant.pk * 111:04d}',
        email=applicant.email,
        highest_qualification=qual,
        institution=inst,
        year_completed=year,
        grade_result=grade,
        years_experience=exp,
        current_employer='Self-employed' if exp < 2 else 'Previous Organization',
        current_position='Casual Worker' if exp < 2 else 'Officer',
        work_history=f'Worked for {exp} years in various capacities including community service and related roles.',
        reference1_name='Rev. Thomas Maino',
        reference1_position='Community Leader',
        reference1_phone='+675 325 1234',
        reference2_name='Mrs. Patricia Konga',
        reference2_position='Former Supervisor',
        reference2_phone='+675 542 5678',
        cover_letter=f'I am writing to apply for the position of {vacancy.title}. '
                     f'I believe my qualifications and experience make me an ideal candidate. '
                     f'I am committed to serving Papua New Guinea and upholding the values of the PNGCS.',
        status=status,
    )
    app.compute_score()
    print(f"  ✓ Application: {applicant.get_full_name()} → {vacancy.reference_number} (Score: {app.total_score})")

    # Add notification
    Notification.objects.create(
        user=applicant,
        title=f'Application Submitted for {vacancy.title}',
        message=f'Your application (Ref: {vacancy.reference_number}) has been received.',
        notification_type='success',
    )

print("\n" + "=" * 60)
print("  DEMO SETUP COMPLETE!")
print("=" * 60)
print("\nLogin credentials:")
print("  HR Admin:    hradmin   / demo1234")
print("  Panel #1:    panelist1 / demo1234")
print("  Panel #2:    panelist2 / demo1234")
print("  Applicant:   john.doe  / demo1234")
print("  Applicant:   jane.smith / demo1234")
print("\nStartup:")
print("  python manage.py runserver 0.0.0.0:8000")
print("=" * 60)
