from django.contrib import admin
from .models import Vacancy, Application, Document, Interview, InterviewScore, Notification, BulkMessage


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'title', 'department', 'province', 'status', 'close_date', 'application_count']
    list_filter = ['status', 'category', 'province']
    search_fields = ['title', 'reference_number', 'department']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'vacancy', 'province', 'status', 'total_score', 'submitted_at']
    list_filter = ['status', 'vacancy', 'province']
    search_fields = ['first_name', 'last_name', 'email']


admin.site.register(Document)
admin.site.register(Interview)
admin.site.register(InterviewScore)
admin.site.register(Notification)
admin.site.register(BulkMessage)
