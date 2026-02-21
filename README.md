# PNGCS Recruitment Portal

A complete Django-based HR recruitment management system for the **Papua New Guinea Correctional Service (PNGCS)**, built by WMX Software.

## Modules

| Module | Description |
|--------|-------------|
| **A — Public Applicant Portal** | Job listings with filtering, digital application form, document uploads |
| **B — Applicant Self-Service Dashboard** | Application tracking, status updates, notifications, document management |
| **C — HR Administration Backend** | Vacancy management, AI scoring, shortlisting, bulk messaging, interview scheduling, reports & Excel export |
| **D — Panel Member Portal** | Restricted interview scoring portal for assigned reviewers |

## Quick Start

```bash
pip install -r requirements.txt
python manage.py migrate
python setup_demo.py        # Creates demo data
python manage.py runserver 0.0.0.0:8000
```

## Demo Login Credentials

| Role | Username | Password | URL |
|------|----------|----------|-----|
| HR Administrator | `hradmin` | `demo1234` | `/hr/` |
| Panel Member | `panelist1` | `demo1234` | `/panel/` |
| Applicant | `john.doe` | `demo1234` | `/dashboard/` |

## Key Features

- **AI-Powered Scoring** — Automated weighted scoring (Education 30%, Grade 25%, Experience 20%, Province 10%, Completeness 15%)
- **Bulk Communication** — Send targeted messages to applicants by vacancy and status
- **Shortlisting Tool** — Score-based shortlisting with one-click bulk approval and applicant notifications
- **Excel Export** — Download shortlist reports as formatted Excel files
- **Role-Based Access** — Applicant / HR Admin / Panel Member roles with separate portals
- **Interview Management** — Schedule interviews, assign panel members, collect scores
- **Analytics Dashboard** — Province distribution, status breakdown, gender stats charts

## Tech Stack

- **Backend:** Django 5.x, SQLite
- **Frontend:** Bootstrap 5.3, Chart.js
- **Reports:** openpyxl (Excel export)

