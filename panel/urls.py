from django.urls import path
from . import views

app_name = 'panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('interview/<int:interview_pk>/', views.application_view, name='application_view'),
]
