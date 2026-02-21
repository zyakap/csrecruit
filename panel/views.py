from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from recruitment.models import Interview, InterviewScore, Application
from accounts.models import ROLE_PANEL
from .forms import InterviewScoreForm


def panel_required(func):
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            if request.user.profile.role not in [ROLE_PANEL, 'panel_member'] and not request.user.is_superuser:
                messages.error(request, 'Access denied. Panel Member role required.')
                return redirect('recruitment:job_list')
        except Exception:
            messages.error(request, 'Access denied.')
            return redirect('recruitment:job_list')
        return func(request, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@panel_required
def dashboard(request):
    interviews = Interview.objects.filter(
        panel_members=request.user,
        status__in=['scheduled', 'completed']
    ).select_related('application__vacancy').order_by('scheduled_date')

    scored_ids = InterviewScore.objects.filter(
        panel_member=request.user
    ).values_list('interview_id', flat=True)

    return render(request, 'panel/dashboard.html', {
        'interviews': interviews,
        'scored_ids': list(scored_ids),
    })


@panel_required
def application_view(request, interview_pk):
    interview = get_object_or_404(Interview, pk=interview_pk, panel_members=request.user)
    application = interview.application
    existing_score = InterviewScore.objects.filter(
        interview=interview, panel_member=request.user
    ).first()

    if request.method == 'POST' and not existing_score:
        form = InterviewScoreForm(request.POST)
        if form.is_valid():
            score_obj = form.save(commit=False)
            score_obj.interview = interview
            score_obj.panel_member = request.user
            score_obj.save()

            interview.status = 'completed'
            interview.save()

            application.status = 'interviewed'
            application.save()

            messages.success(request, 'Interview score submitted successfully.')
            return redirect('panel:dashboard')
    else:
        form = InterviewScoreForm(instance=existing_score) if existing_score else InterviewScoreForm()

    return render(request, 'panel/application_view.html', {
        'interview': interview,
        'application': application,
        'form': form,
        'existing_score': existing_score,
        'documents': application.documents.all(),
    })
