from django.urls import path
from . import views

app_name = 'hr_admin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('vacancies/', views.vacancy_list, name='vacancy_list'),
    path('vacancies/create/', views.vacancy_create, name='vacancy_create'),
    path('vacancies/<int:pk>/edit/', views.vacancy_edit, name='vacancy_edit'),
    path('vacancies/<int:pk>/toggle/', views.vacancy_toggle_status, name='vacancy_toggle'),
    path('vacancies/<int:vacancy_pk>/screen/', views.run_auto_screening, name='run_screening'),
    path('vacancies/<int:vacancy_pk>/shortlist/', views.shortlist_view, name='shortlist'),
    path('vacancies/<int:vacancy_pk>/export/', views.export_shortlist, name='export_shortlist'),
    path('applications/', views.application_list, name='application_list'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('applications/<int:application_pk>/interview/', views.interview_schedule, name='interview_schedule'),
    path('bulk-message/', views.bulk_message, name='bulk_message'),
    path('reports/', views.reports, name='reports'),
]
