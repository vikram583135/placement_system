# core/signals.py

"""
Signal handlers for automated notifications and emails.
Triggers on key events: application status changes, job approvals, interviews scheduled.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import logging

from .models import Application, JobPosting, InterviewSchedule, Notification

logger = logging.getLogger(__name__)


def create_notification(user, message, notification_type='info', link=''):
    """Helper to create a notification for a user."""
    Notification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type,
        link=link
    )


def send_email_safe(subject, message, recipient_list):
    """Send an email, catching errors so they don't break the main flow."""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f"Failed to send email: {e}")


# ==============================================================================
# 1. Application Status Change
# ==============================================================================
@receiver(pre_save, sender=Application)
def track_application_status_change(sender, instance, **kwargs):
    """
    Cache the old status before saving so we can detect changes in post_save.
    """
    if instance.pk:
        try:
            old_instance = Application.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Application.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Application)
def notify_application_status_change(sender, instance, created, **kwargs):
    """
    When an application status changes, notify the student via in-app + email.
    """
    if created:
        # New application — notify company
        company_user = instance.job.company.user
        create_notification(
            user=company_user,
            message=f"New application from {instance.student.user.get_full_name()} for '{instance.job.title}'.",
            notification_type='info',
            link=f"/company/jobs/{instance.job.id}/applicants/"
        )
        return

    old_status = getattr(instance, '_old_status', None)
    if old_status and old_status != instance.status:
        student_user = instance.student.user
        job_title = instance.job.title
        company_name = instance.job.company.name

        # In-app notification for student
        status_messages = {
            'Shortlisted': f"🎉 Congratulations! You've been shortlisted for '{job_title}' at {company_name}.",
            'Interview': f"📅 An interview has been scheduled for '{job_title}' at {company_name}. Check your interview schedule.",
            'Offered': f"🏆 Amazing! You've received an offer for '{job_title}' at {company_name}!",
            'Rejected': f"Your application for '{job_title}' at {company_name} has been updated.",
        }

        status_types = {
            'Shortlisted': 'success',
            'Interview': 'info',
            'Offered': 'success',
            'Rejected': 'warning',
        }

        message = status_messages.get(instance.status, f"Your application status for '{job_title}' changed to {instance.status}.")
        notif_type = status_types.get(instance.status, 'info')

        create_notification(
            user=student_user,
            message=message,
            notification_type=notif_type,
            link='/student/applied-jobs/'
        )

        # Email notification to student
        if student_user.email:
            send_email_safe(
                subject=f"Application Update: {job_title} at {company_name}",
                message=(
                    f"Dear {student_user.get_full_name()},\n\n"
                    f"{message}\n\n"
                    f"Log in to your dashboard for more details.\n\n"
                    f"Best regards,\n"
                    f"PlacementPro Team"
                ),
                recipient_list=[student_user.email],
            )


# ==============================================================================
# 2. Job Posting Approval
# ==============================================================================
@receiver(pre_save, sender=JobPosting)
def track_job_approval_change(sender, instance, **kwargs):
    """Cache old is_approved value."""
    if instance.pk:
        try:
            old_instance = JobPosting.objects.get(pk=instance.pk)
            instance._old_is_approved = old_instance.is_approved
        except JobPosting.DoesNotExist:
            instance._old_is_approved = None
    else:
        instance._old_is_approved = None


@receiver(post_save, sender=JobPosting)
def notify_job_approval(sender, instance, created, **kwargs):
    """
    Notify the company when their job posting is approved.
    """
    if created:
        # New job posted — notify all admins
        from .models import User
        admin_users = User.objects.filter(role='admin')
        for admin_user in admin_users:
            create_notification(
                user=admin_user,
                message=f"New job '{instance.title}' posted by {instance.company.name} awaiting approval.",
                notification_type='warning',
                link='/tpo/jobs/approve/'
            )
        return

    old_approved = getattr(instance, '_old_is_approved', None)
    if old_approved is not None and not old_approved and instance.is_approved:
        # Job just got approved
        company_user = instance.company.user
        create_notification(
            user=company_user,
            message=f"✅ Your job posting '{instance.title}' has been approved and is now visible to students.",
            notification_type='success',
            link='/company/jobs/manage/'
        )

        if company_user.email:
            send_email_safe(
                subject=f"Job Approved: {instance.title}",
                message=(
                    f"Dear {instance.company.name},\n\n"
                    f"Your job posting '{instance.title}' has been approved by the placement cell "
                    f"and is now visible to eligible students.\n\n"
                    f"Best regards,\n"
                    f"PlacementPro Team"
                ),
                recipient_list=[company_user.email],
            )


# ==============================================================================
# 3. Interview Scheduled
# ==============================================================================
@receiver(post_save, sender=InterviewSchedule)
def notify_interview_scheduled(sender, instance, created, **kwargs):
    """
    Notify the student when an interview is scheduled.
    """
    if created:
        student_user = instance.application.student.user
        job_title = instance.application.job.title
        company_name = instance.application.job.company.name

        create_notification(
            user=student_user,
            message=f"📅 Interview scheduled: {instance.round_name} for '{job_title}' at {company_name} on {instance.interview_date}.",
            notification_type='info',
            link='/student/interviews/'
        )

        if student_user.email:
            send_email_safe(
                subject=f"Interview Scheduled: {job_title} at {company_name}",
                message=(
                    f"Dear {student_user.get_full_name()},\n\n"
                    f"An interview has been scheduled for you:\n\n"
                    f"  Position: {job_title}\n"
                    f"  Company: {company_name}\n"
                    f"  Round: {instance.round_name}\n"
                    f"  Date: {instance.interview_date}\n"
                    f"  Time: {instance.interview_time}\n"
                    f"  Mode: {instance.mode}\n"
                    f"  Venue/Link: {instance.venue_or_link}\n\n"
                    f"{'Additional Instructions: ' + instance.additional_instructions if instance.additional_instructions else ''}\n\n"
                    f"Good luck!\n\n"
                    f"Best regards,\n"
                    f"PlacementPro Team"
                ),
                recipient_list=[student_user.email],
            )
