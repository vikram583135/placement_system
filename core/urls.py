# core/urls.py

from django.contrib import admin
from django.urls import path
from core import views

app_name = 'core' # Best practice for namespacing URLs

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Root URL to home view

    # ==============================================================================
    # 1. Generic & Authentication URLs
    # ==============================================================================
    path('about/', views.about, name='about'),
    
    # Auth
    path('register/student/', views.student_register_view, name='register_student'),
    path('register/company/', views.company_register_view, name='register_company'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Note: Password reset URLs are typically included from django.contrib.auth.urls
    # in the project-level urls.py, but are conceptually part of auth.

    # ==============================================================================
    # 2. Student Panel URLs
    # ==============================================================================
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/profile/', views.student_profile_view, name='student_profile'),
    path('student/profile/upload-resume/', views.upload_resume_view, name='upload_resume'),
    path('student/jobs/', views.job_listings_view, name='job_listings'),
    path('student/jobs/<int:job_id>/', views.job_detail_view, name='job_detail'),
    # CORRECTED LINE: Added '=' before 'name'
    path('student/jobs/<int:job_id>/apply/', views.apply_for_job_view, name='apply_for_job'),
    path('student/applied-jobs/', views.applied_jobs_view, name='applied_jobs'),
    path('student/interviews/', views.student_interview_schedule_view, name='interview_schedule'),
    path('student/status/', views.placement_status_view, name='placement_status'),

    # ==============================================================================
    # 3. Company Panel URLs
    # ==============================================================================
    path('company/dashboard/', views.company_dashboard, name='company_dashboard'),
    path('company/profile/', views.company_profile_view, name='company_profile'),
    path('company/jobs/post/', views.post_job_view, name='post_job'),
    path('company/jobs/manage/', views.posted_jobs_view, name='posted_jobs'),
    path('company/jobs/edit/<int:job_id>/', views.edit_job_view, name='edit_job'),
    path('company/jobs/<int:job_id>/applicants/', views.job_applicants_view, name='job_applicants'),
    path('company/jobs/<int:job_id>/shortlist-candidate/<int:application_id>/', views.shortlist_candidate_view, name='shortlist_candidate'),
    path('company/jobs/<int:job_id>/schedule-interviews/', views.schedule_interview_view, name='schedule_interview'),
    path('company/interviews/', views.company_interview_schedules_view, name='company_interview_schedules'),
    path('company/jobs/<int:job_id>/offer/<int:application_id>/', views.offer_candidate_view, name='offer_candidate'),


   # core/urls.py (snippet)

# ==============================================================================
# 4. Admin Panel URLs
# ==============================================================================
path('tpo/dashboard/', views.admin_dashboard, name='admin_dashboard'),
path('tpo/analytics/', views.analytics_view, name='analytics'),
path('tpo/students/', views.manage_students_view, name='manage_students'),
path('tpo/companies/', views.manage_companies_view, name='manage_companies'),
path('tpo/jobs/approve/', views.approve_jobs_view, name='approve_jobs'),
path('tpo/jobs/approve/<int:job_id>/', views.approve_single_job_view, name='approve_single_job'),
path('tpo/jobs/reject/<int:job_id>/', views.reject_single_job_view, name='reject_single_job'),
path('tpo/jobs/all/', views.manage_jobs_view, name='manage_jobs'),
path('tpo/interviews/', views.interview_management_view, name='interview_management'),
path('tpo/reports/', views.generate_reports_view, name='generate_reports'),
path('tpo/reports/export-students-csv/', views.export_students_csv_view, name='export_students_csv'),
path('tpo/reports/export-jobs-csv/', views.export_jobs_csv_view, name='export_jobs_csv'),
path('tpo/upload/', views.bulk_upload_view, name='bulk_upload'),
path('tpo/logs/', views.audit_logs_view, name='audit_logs'),
path('tpo/jobs/approve/', views.approve_jobs_view, name='approve_jobs'),
path('tpo/jobs/approve/<int:job_id>/', views.approve_single_job_view, name='approve_single_job'),
path('tpo/jobs/reject/<int:job_id>/', views.reject_single_job_view, name='reject_single_job'),
# Also change the analytics URL at the bottom of the file

    
    # ==============================================================================
    # 5. Utility & Shared URLs
    # ==============================================================================
    path('notifications/', views.notifications_view, name='notifications'),
    path('chat/', views.chat_view, name='chat'),
    # Note: A real chat app would also require WebSocket routing in asgi.py
    
    path('documents/upload/', views.document_upload_view, name='document_upload'),
    path('documents/delete/<int:doc_id>/', views.delete_document_view, name='delete_document'),
    path('resume/view/<int:student_id>/', views.view_resume_view, name='view_resume'),
    
    # Analytics URL (Typically for Admin)
   
]