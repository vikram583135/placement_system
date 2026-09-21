# core/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, StudentProfile, CompanyProfile, JobPosting,
    Application, InterviewSchedule, Document, AuditLog, Notification
)


# ==============================================================================
# Custom User Admin
# ==============================================================================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model with role field."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_editable = ('role',)

    # Add 'role' to the fieldsets so it appears in the edit form
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )


# ==============================================================================
# Profile Admins
# ==============================================================================
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch', 'cgpa', 'backlogs', 'graduation_year', 'is_placed')
    list_filter = ('branch', 'is_placed', 'graduation_year')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'branch')
    list_editable = ('is_placed',)


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'website', 'is_approved', 'hr_name', 'hr_email')
    list_filter = ('is_approved',)
    search_fields = ('name', 'user__username', 'hr_name', 'hr_email')
    list_editable = ('is_approved',)


# ==============================================================================
# Core Functional Model Admins
# ==============================================================================
@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'salary_range', 'application_deadline', 'is_approved', 'posted_at')
    list_filter = ('is_approved', 'location', 'posted_at')
    search_fields = ('title', 'company__name', 'location', 'description')
    list_editable = ('is_approved',)
    date_hierarchy = 'posted_at'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('student__user__username', 'student__user__first_name', 'job__title', 'job__company__name')
    list_editable = ('status',)
    date_hierarchy = 'applied_at'


# ==============================================================================
# Utility Model Admins
# ==============================================================================
@admin.register(InterviewSchedule)
class InterviewScheduleAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'get_job_title', 'round_name', 'interview_date', 'interview_time', 'mode')
    list_filter = ('mode', 'interview_date')
    search_fields = ('application__student__user__username', 'application__job__title', 'round_name')
    date_hierarchy = 'interview_date'

    @admin.display(description='Student')
    def get_student_name(self, obj):
        return obj.application.student.user.get_full_name()

    @admin.display(description='Job')
    def get_job_title(self, obj):
        return obj.application.job.title


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'file', 'uploaded_at')
    search_fields = ('title',)
    date_hierarchy = 'uploaded_at'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'action')
    date_hierarchy = 'timestamp'
    readonly_fields = ('user', 'action', 'timestamp')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')
    date_hierarchy = 'created_at'
