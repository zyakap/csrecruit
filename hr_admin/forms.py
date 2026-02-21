from django import forms
from django.contrib.auth.models import User
from recruitment.models import Vacancy, Interview, BulkMessage, APPLICATION_STATUS, CATEGORIES, QUALIFICATION_LEVELS
from accounts.models import PROVINCES


class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = [
            'title', 'reference_number', 'department', 'category', 'province',
            'qualification_level', 'positions_available', 'description', 'requirements',
            'min_age', 'max_age', 'salary_range', 'open_date', 'close_date', 'status',
        ]
        widgets = {
            'open_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'close_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'requirements': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.Textarea, forms.DateInput)):
                field.widget.attrs.setdefault('class', 'form-control')
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'


class ApplicationFilterForm(forms.Form):
    vacancy = forms.ModelChoiceField(queryset=Vacancy.objects.all(), required=False,
                                      empty_label='All Vacancies', widget=forms.Select(attrs={'class': 'form-select'}))
    status = forms.ChoiceField(choices=[('', 'All Statuses')] + list(APPLICATION_STATUS), required=False,
                                widget=forms.Select(attrs={'class': 'form-select'}))
    province = forms.ChoiceField(choices=[('', 'All Provinces')] + list(PROVINCES), required=False,
                                  widget=forms.Select(attrs={'class': 'form-select'}))
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name or email'}))


class BulkMessageForm(forms.Form):
    vacancy = forms.ModelChoiceField(
        queryset=Vacancy.objects.all(), required=False,
        empty_label='All Vacancies',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    recipient_status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(APPLICATION_STATUS),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}))


class InterviewScheduleForm(forms.ModelForm):
    panel_members = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(profile__role='panel_member'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Interview
        fields = ['scheduled_date', 'venue', 'panel_members', 'notes']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'venue': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
