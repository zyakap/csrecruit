from django.urls import path
from . import views

app_name = 'recruitment'

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/<int:pk>/apply/', views.apply, name='apply'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_read'),
    path('notifications/read-all/', views.mark_all_read, name='mark_all_read'),
]
