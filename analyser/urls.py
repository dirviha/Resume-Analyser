from django.urls import path
from .views import home, delete_resume, edit_resume, download_report

urlpatterns = [
    path('', home, name='home'),
    path('delete/<int:id>/', delete_resume, name='delete'),
    path('edit/<int:id>/', edit_resume, name='edit'),
    path('report/<int:id>/', download_report, name='report'),
]