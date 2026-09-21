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
    students_list = StudentProfile.objects.all().select_related('user').order_by('user__first_name')
    
    # Search and Filter Logic
    search_query = request.GET.get('search', '')
    branch_filter = request.GET.get('branch', '')
    placed_filter = request.GET.get('placed', '')

    if search_query:
        students_list = students_list.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    if branch_filter:
        students_list = students_list.filter(branch__iexact=branch_filter)
        
    if placed_filter == '1':
        students_list = students_list.filter(is_placed=True)
    elif placed_filter == '0':
        students_list = students_list.filter(is_placed=False)

    # Get distinct branches for filter dropdown
    branches = StudentProfile.objects.values_list('branch', flat=True).distinct()
    paginator = Paginator(students_list, 15) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'students_page_obj': page_obj}
    return render(request, 'admin/manage_students.html', context)


@login_required
@admin_required
def manage_companies_view(request):
    companies_list = CompanyProfile.objects.all().select_related('user').order_by('name')
    
    # Search and Filter Logic
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        companies_list = companies_list.filter(
            Q(name__icontains=search_query) |
            Q(hr_name__icontains=search_query) |
            Q(hr_email__icontains=search_query)
        )
    
    if status_filter == '1':
        companies_list = companies_list.filter(is_approved=True)
    elif status_filter == '0':
        companies_list = companies_list.filter(is_approved=False)

    # Handle inline actions (approve/reject)
    if request.method == 'POST':
        action = request.POST.get('action')
        company_id = request.POST.get('company_id')
        if action and company_id:
            try:
                company = CompanyProfile.objects.get(user_id=company_id)
                if action == 'approve':
                    company.is_approved = True
                    company.save()
                    messages.success(request, f'Company "{company.name}" approved.')
                elif action == 'reject':
                    company.delete()  # Or set to rejected status depending on requirements
                    messages.success(request, 'Company application rejected and removed.')
                return redirect('core:manage_companies')
            except CompanyProfile.DoesNotExist:
                messages.error(request, 'Company not found.')
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
        .annotate(job_count=Count('jobs'))
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

