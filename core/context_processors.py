
# core/context_processors.py

from .models import JobPosting, Notification


def notifications_context(request):
    """
    Makes notification data available to all templates for all user roles.
    """
    if not request.user.is_authenticated:
        return {}

    context = {}

    # Unread notification count (for all authenticated users)
    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    context['unread_notifications_count'] = unread_count

    # Role-specific context
    if request.user.role == 'admin':
        context['pending_jobs_count'] = JobPosting.objects.filter(is_approved=False).count()

    elif request.user.role == 'student':
        from .models import Application, InterviewSchedule
        from django.utils import timezone

        student_profile = getattr(request.user, 'student_profile', None)
        if student_profile:
            # Count of status changes the student hasn't seen (recent updates)
            context['new_updates_count'] = Application.objects.filter(
                student=student_profile,
                status__in=['Shortlisted', 'Interview', 'Offered']
            ).count()

            # Upcoming interviews
            context['upcoming_interviews_count'] = InterviewSchedule.objects.filter(
                application__student=student_profile,
                interview_date__gte=timezone.now().date()
            ).count()

    elif request.user.role == 'company':
        from .models import Application

        company_profile = getattr(request.user, 'company_profile', None)
        if company_profile:
            # New (unreviewed) applications
            context['new_applications_count'] = Application.objects.filter(
                job__company=company_profile,
                status='Applied'
            ).count()

            # Pending job approvals
            context['pending_approval_count'] = JobPosting.objects.filter(
                company=company_profile,
                is_approved=False
            ).count()

    return context