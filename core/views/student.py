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
@student_required
def student_dashboard(request):
    """
    Provides a personalized summary of the student's placement journey.
    """
    student_profile = request.user.student_profile
    
    # Get stats
    applied_jobs_count = Application.objects.filter(student=student_profile).count()
    upcoming_interviews_count = InterviewSchedule.objects.filter(
        application__student=student_profile, 
        interview_date__gte=timezone.now().date()
    ).count()

    # Get recent upcoming interviews
    upcoming_interviews = InterviewSchedule.objects.filter(
        application__student=student_profile,
        interview_date__gte=timezone.now().date()
    ).order_by('interview_date', 'interview_time')[:3]

    # Calculate profile completion
    total_fields = 6 # Total number of fields we're checking for completion
    filled_fields = 0
    if student_profile.phone_number: filled_fields += 1
    if student_profile.resume: filled_fields += 1
    if student_profile.cgpa: filled_fields += 1
    if student_profile.skills: filled_fields += 1
    if student_profile.linkedin_url: filled_fields += 1
    if student_profile.github_url: filled_fields += 1
    
    profile_completion_percentage = int((filled_fields / total_fields) * 100)

    context = {
        'applied_jobs_count': applied_jobs_count,
        'upcoming_interviews_count': upcoming_interviews_count,
        'upcoming_interviews': upcoming_interviews,
        'profile_completion_percentage': profile_completion_percentage,
        'placement_status': "Placed" if student_profile.is_placed else "Not Placed",
    }
    return render(request, 'student/student_dashboard.html', context)


@login_required
@student_required
def student_profile_view(request):
    # This view is already correctly implemented from a previous step
    user_profile = request.user
    student_profile = request.user.student_profile
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user_profile)
        profile_form = StudentProfileForm(request.POST, request.FILES, instance=student_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('core:student_profile')
    else:
        user_form = UserUpdateForm(instance=user_profile)
        profile_form = StudentProfileForm(instance=student_profile)
    context = {'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'student/student_profile.html', context)


@login_required
@student_required
def upload_resume_view(request):
    """
    Handles the resume upload process for the logged-in student.
    """
    # Get the profile instance for the logged-in student
    student_profile = request.user.student_profile

    # This block handles the form submission
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request.
        # Crucially, pass request.FILES to handle the file upload.
        # Pass 'instance' to ensure we are updating the existing profile.
        form = ResumeUploadForm(request.POST, request.FILES, instance=student_profile)
        
        if form.is_valid():
            # The ModelForm's save() method will handle updating the resume field.
            form.save()
            messages.success(request, 'Your resume has been uploaded successfully!')
            # Redirect back to the same page to show the success message
            return redirect('core:upload_resume')
        else:
            messages.error(request, 'There was an error uploading your file. Please try again.')

    # This block handles the initial page visit (GET request)
    else:
        # Create a form instance pre-filled with the student's existing data
        form = ResumeUploadForm(instance=student_profile)
    
    # Create the context dictionary to pass the form and profile to the template
    context = {
        'form': form,
        'student_profile': student_profile # Used to check if a resume already exists
    }
    
    return render(request, 'student/upload_resume.html', context)


@login_required
@student_required
def job_listings_view(request):
    """
    Displays all active, approved jobs for which the student is eligible.
    """
    student_profile = request.user.student_profile
    
    jobs = JobPosting.objects.filter(is_approved=True, application_deadline__gte=timezone.now().date())

    has_applied_subquery = Application.objects.filter(job=OuterRef('pk'), student=student_profile)
    jobs = jobs.annotate(has_applied=Exists(has_applied_subquery))

    eligible_jobs = []
    ineligible_jobs = []

    # ==============================================================================
    # START: REVISED ELIGIBILITY CHECK LOGIC
    # ==============================================================================
    for job in jobs:
        is_eligible = True # Assume eligible by default
        
        # Check CGPA requirement
        # This is the corrected block. It checks if the student's CGPA is None.
        if job.min_cgpa is not None:
            if student_profile.cgpa is None or student_profile.cgpa < job.min_cgpa:
                is_eligible = False
        
        # Check backlogs requirement
        if is_eligible and job.max_backlogs is not None:
            if student_profile.backlogs > job.max_backlogs:
                is_eligible = False
        
        # Check branch requirement
        if is_eligible and job.allowed_branches:
            # Assumes branches are comma-separated with no extra spaces
            allowed_branches_list = [branch.strip() for branch in job.allowed_branches.split(',')]
            if student_profile.branch not in allowed_branches_list:
                is_eligible = False
        
        job.is_eligible = is_eligible
        if is_eligible:
            eligible_jobs.append(job)
        else:
            ineligible_jobs.append(job)
    # ==============================================================================
    # END: REVISED ELIGIBILITY CHECK LOGIC
    # ==============================================================================
    
    # ... (rest of the view for filtering and context) ...
    company_query = request.GET.get('company_name')
    title_query = request.GET.get('title')
    if company_query:
        eligible_jobs = [job for job in eligible_jobs if company_query.lower() in job.company.name.lower()]
    if title_query:
        eligible_jobs = [job for job in eligible_jobs if title_query.lower() in job.title.lower()]

    context = {
        'eligible_jobs': eligible_jobs,
        'ineligible_jobs': ineligible_jobs
    }
    return render(request, 'student/job_listings.html', context)


@login_required
@student_required
def job_detail_view(request, job_id):
    """
    Shows detailed information for a single job and the student's application status for it.
    """
    job = get_object_or_404(JobPosting, id=job_id, is_approved=True)
    student_profile = request.user.student_profile
    
    application_status = "NOT_ELIGIBLE" # Default status
    
    # Check eligibility (with None-safe guards)
    is_eligible = True
    
    if job.min_cgpa is not None:
        if student_profile.cgpa is None or student_profile.cgpa < job.min_cgpa:
            is_eligible = False
    
    if is_eligible and job.max_backlogs is not None:
        if student_profile.backlogs > job.max_backlogs:
            is_eligible = False
    
    if is_eligible and job.allowed_branches:
        allowed_branches_list = [branch.strip() for branch in job.allowed_branches.split(',')]
        if student_profile.branch not in allowed_branches_list:
            is_eligible = False
    
    if is_eligible:
        application_status = "ELIGIBLE"

    # Check if student has already applied
    if Application.objects.filter(job=job, student=student_profile).exists():
        application_status = "APPLIED"
    
    context = {
        'job': job,
        'application_status': application_status
    }
    return render(request, 'student/job_detail.html', context)


@login_required
@student_required
@require_POST # Ensures this view can only be accessed via a POST request
def apply_for_job_view(request, job_id):
    """
    Handles the backend process of applying for a job.
    """
    job = get_object_or_404(JobPosting, id=job_id)
    student_profile = request.user.student_profile
    
    # Backend validation for eligibility (with None-safe guards)
    is_eligible = True
    
    if job.min_cgpa is not None:
        if student_profile.cgpa is None or student_profile.cgpa < job.min_cgpa:
            is_eligible = False
    
    if is_eligible and job.max_backlogs is not None:
        if student_profile.backlogs > job.max_backlogs:
            is_eligible = False
    
    if is_eligible and job.allowed_branches:
        allowed_branches_list = [branch.strip() for branch in job.allowed_branches.split(',')]
        if student_profile.branch not in allowed_branches_list:
            is_eligible = False
    
    # Check for duplicate applications
    already_applied = Application.objects.filter(job=job, student=student_profile).exists()
    
    if not is_eligible:
        messages.error(request, 'You are not eligible to apply for this job.')
    elif already_applied:
        messages.warning(request, 'You have already applied for this job.')
    else:
        Application.objects.create(job=job, student=student_profile, status='Applied')
        messages.success(request, 'You have successfully applied for the job!')
        
    return redirect('core:job_detail', job_id=job.id)


@login_required
@student_required
def applied_jobs_view(request):
    """
    Shows a history of all applications and their current status.
    """
    applications = Application.objects.filter(
        student=request.user.student_profile
    ).select_related('job__company').order_by('-applied_at')
    
    context = {'applications': applications}
    return render(request, 'student/applied_jobs.html', context)


@login_required
@student_required
def student_interview_schedule_view(request):
    """
    Provides the student with a clear schedule of all their interviews.
    """
    interviews = InterviewSchedule.objects.filter(
        application__student=request.user.student_profile
    ).select_related('application__job__company').order_by('interview_date', 'interview_time')
    
    # Annotate with a simple is_past flag for easy styling in template
    for interview in interviews:
        interview.is_past = timezone.now().date() > interview.interview_date

    context = {'interviews': interviews}
    return render(request, 'student/interview_schedule.html', context)


@login_required
@student_required
def placement_status_view(request):
    """
    Shows the student their final placement outcome.
    """
    student_profile = request.user.student_profile
    placement_details = None
    
    if student_profile.is_placed:
        try:
            # Find the application that led to the placement (status = 'Offered')
            placement_details = Application.objects.select_related(
                'job__company'
            ).get(
                student=student_profile, 
                status='Offered'
            )
        except Application.DoesNotExist:
            # Handle case where status might be inconsistent
            placement_details = None
        except Application.MultipleObjectsReturned:
            # If multiple offers exist, get the most recent one
            placement_details = Application.objects.select_related(
                'job__company'
            ).filter(
                student=student_profile, 
                status='Offered'
            ).order_by('-applied_at').first()

    context = {
        'student_profile': student_profile,
        'placement_details': placement_details
    }
    return render(request, 'student/placement_status.html', context)


