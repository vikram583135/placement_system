# core/views.py

from django.shortcuts import render, redirect
from django.http import HttpResponse # Useful for simple placeholder responses
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import student_required, company_required, admin_required
from .forms import BulkUploadForm, StudentRegistrationForm, CompanyRegistrationForm, UserUpdateForm, StudentProfileForm, CompanyProfileForm, JobPostingForm, ResumeUploadForm, InterviewScheduleForm
from django.contrib.auth.forms import AuthenticationForm
from .models import User, StudentProfile, CompanyProfile, JobPosting, Application, InterviewSchedule, Document, AuditLog
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Exists, OuterRef
from django.shortcuts import render, redirect, get_object_or_404
import csv
import io
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from datetime import date
from django.utils import timezone
from django.views.decorators.http import require_POST
# ==============================================================================
# 1. Generic & Authentication Views
# ==============================================================================

# core/views.py

def home(request):
    """
    Handles the homepage and role-based redirection for logged-in users.
    """
    # This block handles all logged-in users
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('core:admin_dashboard')
        elif request.user.role == 'student':
            return redirect('core:student_dashboard')
        elif request.user.role == 'company':
            return redirect('core:company_dashboard')
    
    # This line is now OUTSIDE the 'if' block.
    # It will only be reached if the user is NOT authenticated.
    return render(request, 'home.html')

def about(request):
    """Renders the about page."""
    return render(request, 'about.html')

# --- Auth Views ---
def student_register_view(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student account created! You can now log in.')
            return redirect('core:login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'registration/register_student.html', {'form': form})

def company_register_view(request):
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company account created! You can now log in.')
            return redirect('core:login')
    else:
        form = CompanyRegistrationForm()
    return render(request, 'registration/register_company.html', {'form': form})

# core/views.py

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('core:home')
            else:
                # This adds the error message for the template to display
                messages.error(request, 'Invalid username or password.')
        # If the form is invalid, Django and crispy-forms will handle
        # displaying the errors on the form fields themselves.
    
    # This block now only runs for the initial visit (GET request)
    else:
        form = AuthenticationForm()

    # Pass the form (either blank or with errors) to the template
    return render(request, 'registration/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('core:home')

# ==============================================================================
# 2. Student Panel Views
# ==============================================================================

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
    
    # Check eligibility
    is_eligible = (
        student_profile.cgpa >= job.min_cgpa and
        student_profile.backlogs <= job.max_backlogs and
        student_profile.branch in job.allowed_branches.split(',')
    )
    
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
    
    # Backend validation for eligibility
    is_eligible = (
        student_profile.cgpa >= job.min_cgpa and
        student_profile.backlogs <= job.max_backlogs and
        student_profile.branch in job.allowed_branches.split(',')
    )
    
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

# ==============================================================================
# 3. Company Panel Views
# ==============================================================================

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
    
    # Handle individual action buttons (GET requests)
    if request.method == 'GET':
        action = request.GET.get('action')
        app_id = request.GET.get('app_id')
        
        if action and app_id:
            try:
                application = Application.objects.get(id=app_id, job=job)
                if action == 'shortlist':
                    application.status = 'Shortlisted'
                    application.save()
                    messages.success(request, f'{application.student.user.get_full_name()} has been shortlisted.')
                elif action == 'reject':
                    application.status = 'Rejected'
                    application.save()
                    messages.warning(request, f'{application.student.user.get_full_name()} has been rejected.')
                return redirect('core:job_applicants', job_id=job.id)
            except Application.DoesNotExist:
                messages.error(request, 'Application not found.')
    
    # Handle bulk actions (POST requests)
    if request.method == 'POST':
        app_ids = request.POST.getlist('selected_applications')
        action = request.POST.get('action')
        
        if app_ids and action:
            selected_applications = Application.objects.filter(id__in=app_ids)
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


# ==============================================================================
# 4. Admin Panel Views
# ==============================================================================

# The CORRECT and complete version of the function
@login_required
@admin_required
def admin_dashboard(request):
    # This view is already implemented correctly
    student_count = StudentProfile.objects.count()
    placed_count = StudentProfile.objects.filter(is_placed=True).count()
    unplaced_count = student_count - placed_count
    company_count = CompanyProfile.objects.count()
    pending_jobs_count = JobPosting.objects.filter(is_approved=False).count()
    context = {
        'student_count': student_count,
        'placed_count': placed_count,
        'unplaced_count': unplaced_count,
        'company_count': company_count,
        'pending_jobs_count': pending_jobs_count,
    }
    return render(request, 'admin/admin_dashboard.html', context)

@login_required
@admin_required
def manage_students_view(request):
    # This view is already implemented correctly
    students_list = StudentProfile.objects.all().select_related('user').order_by('user__first_name')
    # ... (filtering and pagination logic) ...
    paginator = Paginator(students_list, 15) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'students_page_obj': page_obj}
    return render(request, 'admin/manage_students.html', context)


@login_required
@admin_required
def manage_companies_view(request):
    # This view is already implemented correctly
    companies_list = CompanyProfile.objects.all().select_related('user').order_by('name')
    # ... (filtering and pagination logic) ...
    paginator = Paginator(companies_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'companies_page_obj': page_obj}
    return render(request, 'admin/manage_companies.html', context)


@login_required
@admin_required
def approve_jobs_view(request):
    # This view is already implemented correctly
    pending_jobs = JobPosting.objects.filter(is_approved=False).select_related('company').order_by('-posted_at')
    context = {'pending_jobs': pending_jobs}
    return render(request, 'admin/approve_jobs.html', context)


@login_required
@admin_required
def approve_single_job_view(request, job_id):
    # This view is already implemented correctly
    if request.method == 'POST':
        job = get_object_or_404(JobPosting, id=job_id)
        job.is_approved = True
        job.save()
        messages.success(request, f'Job "{job.title}" has been approved.')
    return redirect('core:approve_jobs')


@login_required
@admin_required
def reject_single_job_view(request, job_id):
    # This view is already implemented correctly
    if request.method == 'POST':
        job = get_object_or_404(JobPosting, id=job_id)
        job_title = job.title
        job.delete()
        messages.warning(request, f'Job "{job_title}" has been rejected and deleted.')
    return redirect('core:approve_jobs')


# --- START: NEWLY IMPLEMENTED VIEWS ---

@login_required
@admin_required
def manage_jobs_view(request):
    """
    Displays a master list of all jobs with filters and pagination.
    """
    jobs_list = JobPosting.objects.all().select_related('company').prefetch_related('applications').order_by('-posted_at')

    # Filtering
    title_query = request.GET.get('title')
    company_query = request.GET.get('company')
    if title_query:
        jobs_list = jobs_list.filter(title__icontains=title_query)
    if company_query:
        jobs_list = jobs_list.filter(company__name__icontains=company_query)

    paginator = Paginator(jobs_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'all_jobs_page_obj': page_obj,
        'today': date.today() # Pass today's date for status checking
    }
    return render(request, 'admin/manage_jobs.html', context)


@login_required
@admin_required
def interview_management_view(request):
    """
    Provides a global view of all scheduled interviews.
    """
    interviews_list = InterviewSchedule.objects.all().select_related(
        'application__job__company', 
        'application__student__user'
    ).order_by('-interview_date', '-interview_time')

    # Basic filtering example
    company_query = request.GET.get('company')
    if company_query:
        interviews_list = interviews_list.filter(application__job__company__name__icontains=company_query)

    paginator = Paginator(interviews_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'interviews_page_obj': page_obj
    }
    return render(request, 'admin/interview_management.html', context)


@login_required
@admin_required
def generate_reports_view(request):
    """
    Renders the page with options to download reports.
    """
    return render(request, 'admin/generate_reports.html')


@login_required
@admin_required
def export_students_csv_view(request):
    """
    Handles the logic for exporting student data to a CSV file.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Username', 'First Name', 'Last Name', 'Email', 'Branch', 'CGPA', 'Backlogs', 'Placed Status'])

    # Apply filters from GET request if they exist
    students = StudentProfile.objects.all().select_related('user')
    branch_query = request.GET.get('branch')
    status_query = request.GET.get('status')
    if branch_query:
        students = students.filter(branch__icontains=branch_query)
    if status_query:
        is_placed = True if status_query == 'placed' else False
        students = students.filter(is_placed=is_placed)

    for student in students:
        writer.writerow([
            student.user.username,
            student.user.first_name,
            student.user.last_name,
            student.user.email,
            student.branch,
            student.cgpa,
            student.backlogs,
            'Placed' if student.is_placed else 'Not Placed'
        ])
    
    return response
@login_required
@admin_required
def export_jobs_csv_view(request):
    """
    Handles the logic for exporting job posting data to a CSV file.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="jobs_report.csv"'

    writer = csv.writer(response)
    # Define the CSV headers
    writer.writerow([
        'Job Title', 
        'Company', 
        'Location', 
        'Salary Range', 
        'Deadline',
        'Status',
        'Applicant Count'
    ])

    # Get all jobs and their related company/application info efficiently
    jobs = JobPosting.objects.all().select_related('company').prefetch_related('applications')
    
    # You can add filtering logic here later based on request.GET parameters if needed

    for job in jobs:
        status = 'Pending'
        if job.is_approved:
            # Check if the date is in the past
            if date.today() > job.application_deadline:
                 status = 'Closed'
            else:
                 status = 'Open'

        writer.writerow([
            job.title,
            job.company.name,
            job.location,
            job.salary_range,
            job.application_deadline,
            status,
            job.applications.count()
        ])
    
    return response


@login_required
@admin_required
def bulk_upload_view(request):
    """
    Handles the logic for bulk uploading data from a CSV file.
    """
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            upload_type = form.cleaned_data['upload_type']
            
            # Use io.TextIOWrapper to decode the file in memory
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string)
            next(reader) # Skip the header row

            try:
                with transaction.atomic(): # Ensures that if one row fails, all are rolled back
                    if upload_type == 'students':
                        for row in reader:
                            username, password, email, first_name, last_name, branch, cgpa, backlogs = row
                            user = User.objects.create_user(
                                username=username,
                                password=password,
                                email=email,
                                first_name=first_name,
                                last_name=last_name,
                                role='student'
                            )
                            StudentProfile.objects.create(
                                user=user,
                                branch=branch,
                                cgpa=float(cgpa),
                                backlogs=int(backlogs)
                            )
                messages.success(request, f"Successfully uploaded {upload_type} data.")
            except Exception as e:
                messages.error(request, f"An error occurred during upload: {e}")

            return redirect('core:admin_dashboard')
    else:
        form = BulkUploadForm()
        
    return render(request, 'admin/bulk_upload.html', {'form': form})


@login_required
@admin_required
def audit_logs_view(request):
    """
    Displays a paginated list of all audit log entries.
    """
    logs_list = AuditLog.objects.all().select_related('user').order_by('-timestamp')
    
    paginator = Paginator(logs_list, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'logs_page_obj': page_obj}
    return render(request, 'admin/audit_logs.html', context)


@login_required
@admin_required
def analytics_view(request):
    """
    Gathers data and passes it to the analytics page for chart rendering.
    """
    # Example 1: Placement stats by branch
    branch_stats = StudentProfile.objects.values('branch').annotate(
        total=Count('user'),
        placed=Count('user', filter=Q(is_placed=True))
    ).order_by('-total')

    # Example 2: Company engagement by jobs posted
    company_stats = CompanyProfile.objects.annotate(
        job_count=Count('jobs')
    ).order_by('-job_count')[:10] # Top 10 companies

    # Format data for Chart.js
    branch_labels = [stat['branch'] for stat in branch_stats]
    branch_total_data = [stat['total'] for stat in branch_stats]
    branch_placed_data = [stat['placed'] for stat in branch_stats]

    company_labels = [stat.name for stat in company_stats]
    company_job_counts = [stat.job_count for stat in company_stats]

    context = {
        'branch_labels': JsonResponse(branch_labels, safe=False).content.decode(),
        'branch_total_data': JsonResponse(branch_total_data, safe=False).content.decode(),
        'branch_placed_data': JsonResponse(branch_placed_data, safe=False).content.decode(),
        'company_labels': JsonResponse(company_labels, safe=False).content.decode(),
        'company_job_counts': JsonResponse(company_job_counts, safe=False).content.decode(),
    }
    return render(request, 'admin/analytics.html', context)

# ==============================================================================
# 5. Utility & Shared Views
# ==============================================================================

@login_required
def notifications_view(request):
    """
    Displays a list of notifications for the logged-in user.
    """
    # TODO: Add logic here to fetch notification objects from the database
    # that are specific to the request.user.
    # For now, we will just pass an empty context.
    
    # Example logic you might add later:
    # notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    # context = {'notifications': notifications}
    
    context = {} # Using an empty context for now
    
    return render(request, 'notifications.html', context)
@login_required
def chat_view(request):
    return render(request, 'chat.html')

@login_required
@admin_required # Or make it accessible to others if needed
def document_upload_view(request):
    return render(request, 'admin/document_upload.html')

@login_required
@admin_required
def delete_document_view(request, doc_id):
    messages.success(request, 'Document deleted.')
    return redirect('core:document_upload')

@login_required
def view_resume_view(request, student_id):
    # Add logic to fetch student's resume URL
    return render(request, 'utils/view_resume.html')

@login_required
@admin_required
@admin_required
def analytics_view(request):
    """
    Advanced Analytics Dashboard for Admin/TPO
    Shows placement statistics, company engagement, and trends
    """
    from django.db.models import Count, Q
    import json
    
    # 1. Placement Rate by Branch
    branches = ['Computer Science Engineering', 'Electronics and Communication Engineering', 
                'Mechanical Engineering', 'Electrical and Electronics Engineering', 
                'Civil Engineering', 'Chemical Engineering']
    
    branch_labels = []
    branch_total_data = []
    branch_placed_data = []
    
    for branch in branches:
        total = StudentProfile.objects.filter(branch=branch).count()
        placed = StudentProfile.objects.filter(branch=branch, is_placed=True).count()
        
        if total > 0:  # Only include branches with students
            # Use abbreviated names for better chart display
            branch_short = {
                'Computer Science Engineering': 'CSE',
                'Electronics and Communication Engineering': 'ECE',
                'Mechanical Engineering': 'ME',
                'Electrical and Electronics Engineering': 'EEE',
                'Civil Engineering': 'Civil',
                'Chemical Engineering': 'Chemical'
            }.get(branch, branch)
            
            branch_labels.append(branch_short)
            branch_total_data.append(total)
            branch_placed_data.append(placed)
    
    # 2. Top Companies by Jobs Posted
    top_companies = (
        CompanyProfile.objects
        .annotate(job_count=Count('jobposting'))
        .filter(job_count__gt=0)
        .order_by('-job_count')[:10]
    )
    
    company_labels = [company.name for company in top_companies]
    company_job_counts = [company.job_count for company in top_companies]
    
    # 3. Application Status Distribution
    application_statuses = Application.objects.values('status').annotate(count=Count('id'))
    status_labels = [item['status'] for item in application_statuses]
    status_counts = [item['count'] for item in application_statuses]
    
    # 4. Monthly Placement Trends (last 6 months)
    from datetime import datetime, timedelta
    from django.db.models.functions import TruncMonth
    
    six_months_ago = datetime.now() - timedelta(days=180)
    
    monthly_applications = (
        Application.objects
        .filter(applied_at__gte=six_months_ago)
        .annotate(month=TruncMonth('applied_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    trend_labels = [item['month'].strftime('%B %Y') for item in monthly_applications]
    trend_counts = [item['count'] for item in monthly_applications]
    
    # 5. CGPA Distribution of Placed vs Non-Placed Students
    cgpa_ranges = [
        (6.0, 6.99, '6.0-6.9'),
        (7.0, 7.99, '7.0-7.9'),
        (8.0, 8.99, '8.0-8.9'),
        (9.0, 10.0, '9.0-10.0')
    ]
    
    cgpa_labels = [label for _, _, label in cgpa_ranges]
    cgpa_placed = []
    cgpa_not_placed = []
    
    for min_cgpa, max_cgpa, _ in cgpa_ranges:
        placed = StudentProfile.objects.filter(
            cgpa__gte=min_cgpa,
            cgpa__lte=max_cgpa,
            is_placed=True
        ).count()
        
        not_placed = StudentProfile.objects.filter(
            cgpa__gte=min_cgpa,
            cgpa__lte=max_cgpa,
            is_placed=False
        ).count()
        
        cgpa_placed.append(placed)
        cgpa_not_placed.append(not_placed)
    
    # 6. Interview Conversion Rates
    interview_statuses = ['Shortlisted', 'Interview', 'Offered']
    interview_counts = []
    
    for status in interview_statuses:
        count = Application.objects.filter(status=status).count()
        interview_counts.append(count)
    
    # Convert to JSON for safe template rendering
    context = {
        'branch_labels': json.dumps(branch_labels),
        'branch_total_data': json.dumps(branch_total_data),
        'branch_placed_data': json.dumps(branch_placed_data),
        
        'company_labels': json.dumps(company_labels),
        'company_job_counts': json.dumps(company_job_counts),
        
        'status_labels': json.dumps(status_labels),
        'status_counts': json.dumps(status_counts),
        
        'trend_labels': json.dumps(trend_labels),
        'trend_counts': json.dumps(trend_counts),
        
        'cgpa_labels': json.dumps(cgpa_labels),
        'cgpa_placed': json.dumps(cgpa_placed),
        'cgpa_not_placed': json.dumps(cgpa_not_placed),
        
        'interview_statuses': json.dumps(interview_statuses),
        'interview_counts': json.dumps(interview_counts),
        
        # Summary statistics
        'total_students': StudentProfile.objects.count(),
        'placed_students': StudentProfile.objects.filter(is_placed=True).count(),
        'total_companies': CompanyProfile.objects.filter(is_approved=True).count(),
        'total_jobs': JobPosting.objects.filter(is_approved=True).count(),
        'total_applications': Application.objects.count(),
        'total_interviews': InterviewSchedule.objects.count(),
    }
    
    # Calculate placement percentage
    if context['total_students'] > 0:
        context['placement_percentage'] = round(
            (context['placed_students'] / context['total_students']) * 100, 2
        )
    else:
        context['placement_percentage'] = 0
    
    return render(request, 'admin/analytics.html', context)