from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import student_required, company_required, admin_required
from core.forms import (
    BulkUploadForm, StudentRegistrationForm, CompanyRegistrationForm,
    UserUpdateForm, StudentProfileForm, CompanyProfileForm,
    JobPostingForm, ResumeUploadForm, InterviewScheduleForm, PasswordChangeCustomForm
)
from django.contrib.auth.forms import AuthenticationForm
from core.models import (
    User, StudentProfile, CompanyProfile, JobPosting,
    Application, InterviewSchedule, Document, AuditLog
)
from django.core.paginator import Paginator
from django.db.models import Q, Exists, OuterRef, Count
from django.db import transaction
import csv
import io
from datetime import date
from django.utils import timezone
from django.views.decorators.http import require_POST

@login_required
@company_required
def company_dashboard(request):
    """
    Provides a high-level summary of the company's recruitment activities.
    """
    company_profile = request.user.company_profile
    
    # Get stats for dashboard cards
    total_jobs_posted = JobPosting.objects.filter(company=company_profile, is_approved=True).count()
    total_applications = Application.objects.filter(job__company=company_profile).count()
    shortlisted_candidates = Application.objects.filter(job__company=company_profile, status='Shortlisted').count()

    # Get recent jobs
    recent_jobs = JobPosting.objects.filter(company=company_profile).order_by('-posted_at')[:5]

    # Data for the "Applications per Job" chart
    jobs_with_app_counts = JobPosting.objects.filter(company=company_profile, is_approved=True).annotate(
        application_count=Count('applications')
    ).order_by('-application_count')

    job_titles = [job.title for job in jobs_with_app_counts]
    job_app_counts = [job.application_count for job in jobs_with_app_counts]
    
    context = {
        'total_jobs_posted': total_jobs_posted,
        'total_applications': total_applications,
        'shortlisted_candidates': shortlisted_candidates,
        'recent_jobs': recent_jobs,
        'job_titles_json': JsonResponse(job_titles, safe=False).content.decode(),
        'job_app_counts_json': JsonResponse(job_app_counts, safe=False).content.decode(),
    }
    return render(request, 'company/company_dashboard.html', context)


@login_required
@company_required
def company_profile_view(request):
    # This view is already correctly implemented
    profile_instance = request.user.company_profile
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your company profile has been updated successfully!')
            return redirect('core:company_profile')
    else:
        form = CompanyProfileForm(instance=profile_instance)
    context = {'form': form, 'company_profile': profile_instance}
    return render(request, 'company/company_profile.html', context)


@login_required
@company_required
def post_job_view(request):
    # This view is already correctly implemented
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = request.user.company_profile
            job.save()
            messages.success(request, 'Job posted! It is now pending admin approval.')
            return redirect('core:posted_jobs')
    else:
        form = JobPostingForm()
    context = {'form': form}
    return render(request, 'company/post_job.html', context)


@login_required
@company_required
def posted_jobs_view(request):
    """
    Displays a list of all jobs the company has posted.
    """
    company_profile = request.user.company_profile
    jobs = JobPosting.objects.filter(company=company_profile).prefetch_related('applications').order_by('-posted_at')
    
    paginator = Paginator(jobs, 10) # Show 10 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'jobs_page_obj': page_obj,
        'today': timezone.now().date()
    }
    return render(request, 'company/posted_jobs.html', context)


@login_required
@company_required
def edit_job_view(request, job_id):
    """
    Handles editing an existing job posting.
    """
    job = get_object_or_404(JobPosting, id=job_id, company=request.user.company_profile)
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job posting has been updated successfully!')
            return redirect('core:posted_jobs')
    else:
        form = JobPostingForm(instance=job)
    
    context = {'form': form}
    # Uses the same template as post_job.html
    return render(request, 'company/post_job.html', context)


@login_required
@company_required
def job_applicants_view(request, job_id):
    """
    Displays applicants for a specific job and handles bulk status changes.
    """
    job = get_object_or_404(JobPosting, id=job_id, company=request.user.company_profile)
    
    # Handle all actions via POST only (individual + bulk)
    if request.method == 'POST':
        # Check for individual action
        individual_app_id = request.POST.get('app_id')
        individual_action = request.POST.get('individual_action')
        
        if individual_app_id and individual_action:
            try:
                application = Application.objects.get(id=individual_app_id, job=job)
                if individual_action == 'shortlist':
                    application.status = 'Shortlisted'
                    application.save()
                    messages.success(request, f'{application.student.user.get_full_name()} has been shortlisted.')
                elif individual_action == 'reject':
                    application.status = 'Rejected'
                    application.save()
                    messages.warning(request, f'{application.student.user.get_full_name()} has been rejected.')
                return redirect('core:job_applicants', job_id=job.id)
            except Application.DoesNotExist:
                messages.error(request, 'Application not found.')
        
        # Check for bulk action
        app_ids = request.POST.getlist('selected_applications')
        action = request.POST.get('action')
        
        if app_ids and action:
            selected_applications = Application.objects.filter(id__in=app_ids, job=job)
            if action == 'shortlist':
                updated_count = selected_applications.update(status='Shortlisted')
                messages.success(request, f'{updated_count} candidate(s) have been shortlisted.')
            elif action == 'reject':
                updated_count = selected_applications.update(status='Rejected')
                messages.warning(request, f'{updated_count} candidate(s) have been rejected.')
            return redirect('core:job_applicants', job_id=job.id)

    applications = Application.objects.filter(job=job).select_related('student__user').order_by('-applied_at')
    context = {
        'job': job,
        'applications': applications
    }
    return render(request, 'company/job_applicants.html', context)


@login_required
@company_required
def shortlist_candidate_view(request, job_id, application_id):
    # This can be handled by the main job_applicants_view now,
    # but we'll keep it as a simple redirect for any old links.
    # The main logic is now handled in bulk in job_applicants_view.
    if request.GET.get('action') == 'shortlist':
        Application.objects.filter(id=application_id).update(status='Shortlisted')
        messages.success(request, 'Candidate shortlisted.')
    elif request.GET.get('action') == 'reject':
        Application.objects.filter(id=application_id).update(status='Rejected')
        messages.warning(request, 'Candidate rejected.')
    return redirect('core:job_applicants', job_id=job_id)


@login_required
@company_required
def schedule_interview_view(request, job_id):
    """
    Handles scheduling interviews for all shortlisted candidates for a job.
    """
    job = get_object_or_404(JobPosting, id=job_id, company=request.user.company_profile)
    shortlisted_applications = Application.objects.filter(job=job, status='Shortlisted')

    if request.method == 'POST':
        form = InterviewScheduleForm(request.POST)
        if form.is_valid():
            try:
                # Use a transaction to ensure all or nothing is saved
                with transaction.atomic():
                    for app in shortlisted_applications:
                        InterviewSchedule.objects.create(
                            application=app,
                            interview_date=form.cleaned_data['interview_date'],
                            interview_time=form.cleaned_data['interview_time'],
                            round_name=form.cleaned_data['round_name'],
                            venue_or_link=form.cleaned_data['venue_or_link']
                        )
                    
                    # Update status for all shortlisted candidates at once
                    updated_count = shortlisted_applications.update(status='Interview')
                messages.success(request, f'Successfully scheduled interviews for {updated_count} candidates.')
                return redirect('core:company_dashboard')
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")

    else:
        form = InterviewScheduleForm()
        
    context = {
        'job': job,
        'shortlisted_applications': shortlisted_applications,
        'form': form
    }
    return render(request, 'company/schedule_interview.html', context) # You would need to create this template


@login_required
@company_required
def company_interview_schedules_view(request):
    """
    Displays a list of all interviews scheduled by the company.
    """
    company_profile = request.user.company_profile
    
    # Fetch all interviews for jobs posted by this company
    interviews = InterviewSchedule.objects.filter(
        application__job__company=company_profile
    ).select_related(
        'application__job',
        'application__student__user'
    ).order_by('interview_date', 'interview_time')

    context = {
        'interviews': interviews
    }
    return render(request, 'company/interview_schedules.html', context)


@login_required
@company_required
@require_POST # Ensures this view only accepts POST requests
@transaction.atomic # Ensures both database updates succeed or fail together
def offer_candidate_view(request, job_id, application_id):
    """
    Handles the action of marking a candidate as 'Offered'.
    This view updates both the Application status and the Student's profile.
    """
    try:
        # Get the specific application, ensuring it belongs to the current company
        application = get_object_or_404(
            Application, 
            id=application_id, 
            job__id=job_id,
            job__company=request.user.company_profile
        )
        
        # Get the related student profile
        student_profile = application.student
        
        # Set the student's main profile status to placed
        student_profile.is_placed = True
        student_profile.save()
        
        # Update the application status to 'Offered'
        application.status = 'Offered'
        application.save()
        
        # Update all other applications for this student to 'Rejected' or keep them as is
        # (Optional: You can reject other pending applications automatically)
        Application.objects.filter(
            student=student_profile
        ).exclude(
            id=application_id
        ).exclude(
            status__in=['Offered', 'Rejected']
        ).update(status='Rejected')
        
        # Create audit log entry
        AuditLog.objects.create(
            user=request.user,
            action=f'Extended offer to {student_profile.user.get_full_name()} for {application.job.title}'
        )
        
        messages.success(request, f'An offer has been successfully extended to {student_profile.user.get_full_name()}!')
        
    except Exception as e:
        messages.error(request, f'Error extending offer: {str(e)}')
        print(f'ERROR in offer_candidate_view: {e}')  # This will appear in the terminal
    
    return redirect('core:job_applicants', job_id=job_id)


