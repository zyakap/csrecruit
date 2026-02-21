from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Vacancy, Application, Document, Notification, CATEGORIES, QUALIFICATION_LEVELS
from .forms import ApplicationForm, DocumentUploadForm
from accounts.models import PROVINCES


def job_list(request):
    vacancies = Vacancy.objects.filter(status='open')
    province_filter = request.GET.get('province', '')
    category_filter = request.GET.get('category', '')
    qual_filter = request.GET.get('qualification', '')
    search = request.GET.get('search', '')

    if province_filter:
        vacancies = vacancies.filter(province__in=[province_filter, 'All'])
    if category_filter:
        vacancies = vacancies.filter(category=category_filter)
    if qual_filter:
        vacancies = vacancies.filter(qualification_level=qual_filter)
    if search:
        vacancies = vacancies.filter(
            Q(title__icontains=search) | Q(description__icontains=search) | Q(department__icontains=search)
        )

    today = timezone.now().date()
    vacancies = [v for v in vacancies if v.open_date <= today <= v.close_date]

    context = {
        'vacancies': vacancies,
        'provinces': PROVINCES,
        'categories': CATEGORIES,
        'qualifications': QUALIFICATION_LEVELS,
        'province_filter': province_filter,
        'category_filter': category_filter,
        'qual_filter': qual_filter,
        'search': search,
    }
    return render(request, 'recruitment/job_list.html', context)


def job_detail(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, status='open')
    already_applied = False
    if request.user.is_authenticated:
        already_applied = Application.objects.filter(vacancy=vacancy, applicant=request.user).exists()
    return render(request, 'recruitment/job_detail.html', {
        'vacancy': vacancy,
        'already_applied': already_applied,
    })


@login_required
def apply(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, status='open')
    today = timezone.now().date()
    if not (vacancy.open_date <= today <= vacancy.close_date):
        messages.error(request, 'This vacancy is no longer accepting applications.')
        return redirect('recruitment:job_detail', pk=pk)

    if Application.objects.filter(vacancy=vacancy, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this position.')
        return redirect('recruitment:dashboard')

    profile = request.user.profile
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.vacancy = vacancy
            application.applicant = request.user
            application.status = 'submitted'
            application.save()

            application.compute_score()

            files = request.FILES.getlist('documents')
            doc_types = request.POST.getlist('doc_types')
            for i, f in enumerate(files):
                dtype = doc_types[i] if i < len(doc_types) else 'other'
                Document.objects.create(
                    application=application,
                    doc_type=dtype,
                    file=f,
                    filename=f.name,
                )

            Notification.objects.create(
                user=request.user,
                title='Application Submitted Successfully',
                message=f'Your application for {vacancy.title} (Ref: {vacancy.reference_number}) has been received. '
                        f'Your application reference is #{application.pk}. We will keep you updated on progress.',
                notification_type='success',
            )

            messages.success(request, f'Application submitted successfully! Reference: #{application.pk}')
            return redirect('recruitment:dashboard')
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': profile.phone,
            'province': profile.province,
            'gender': profile.gender,
            'date_of_birth': profile.date_of_birth,
        }
        form = ApplicationForm(initial=initial)

    return render(request, 'recruitment/apply.html', {
        'form': form,
        'vacancy': vacancy,
    })


@login_required
def dashboard(request):
    applications = Application.objects.filter(applicant=request.user).select_related('vacancy')
    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(read=False).count()
    return render(request, 'recruitment/dashboard.html', {
        'applications': applications,
        'notifications': notifications[:10],
        'unread_count': unread_count,
    })


@login_required
def application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk, applicant=request.user)
    documents = application.documents.all()
    interviews = application.interviews.all()

    if request.method == 'POST':
        files = request.FILES.getlist('documents')
        doc_types = request.POST.getlist('doc_types')
        for i, f in enumerate(files):
            dtype = doc_types[i] if i < len(doc_types) else 'other'
            Document.objects.create(
                application=application,
                doc_type=dtype,
                file=f,
                filename=f.name,
            )
        messages.success(request, 'Documents uploaded successfully.')
        return redirect('recruitment:application_detail', pk=pk)

    return render(request, 'recruitment/application_detail.html', {
        'application': application,
        'documents': documents,
        'interviews': interviews,
    })


@login_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.read = True
    notif.save()
    return redirect('recruitment:dashboard')


@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    return redirect('recruitment:dashboard')
