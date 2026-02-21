from django import forms
from recruitment.models import InterviewScore


class InterviewScoreForm(forms.ModelForm):
    class Meta:
        model = InterviewScore
        fields = [
            'communication_score', 'knowledge_score',
            'attitude_score', 'experience_score',
            'comments', 'recommendation',
        ]
        widgets = {
            'communication_score': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 0, 'max': 20, 'step': 0.5
            }),
            'knowledge_score': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 0, 'max': 30, 'step': 0.5
            }),
            'attitude_score': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 0, 'max': 25, 'step': 0.5
            }),
            'experience_score': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 0, 'max': 25, 'step': 0.5
            }),
            'comments': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'recommendation': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'communication_score': 'Communication Skills (out of 20)',
            'knowledge_score': 'Job Knowledge & Technical Skills (out of 30)',
            'attitude_score': 'Attitude & Professionalism (out of 25)',
            'experience_score': 'Relevant Experience (out of 25)',
        }
