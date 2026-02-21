from django import forms
from .models import Application, Document, QUALIFICATION_LEVELS, PROVINCES, GENDER_CHOICES


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'province', 'address', 'phone', 'email', 'nationality',
            'highest_qualification', 'institution', 'year_completed', 'grade_result',
            'years_experience', 'current_employer', 'current_position', 'work_history',
            'reference1_name', 'reference1_position', 'reference1_phone',
            'reference2_name', 'reference2_position', 'reference2_phone',
            'cover_letter',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'work_history': forms.Textarea(attrs={'rows': 3}),
            'cover_letter': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-control')


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['doc_type', 'file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doc_type'].widget.attrs['class'] = 'form-select'
