# core/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

# ==============================================================================
# 1. Custom User Model
# ==============================================================================
class User(AbstractUser):
    """
    Custom User model to include a 'role' for differentiating between
    Admins, Students, and Companies.
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('company', 'Company'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

# ==============================================================================
# 2. Profile Models (Extending the User Model)
# ==============================================================================
class StudentProfile(models.Model):
    """
    Stores all data specific to a student. Linked one-to-one with the User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='student_profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True, help_text="Upload your resume in PDF format.")
    cgpa = models.FloatField(null=True, blank=True)
    branch = models.CharField(max_length=100)
    graduation_year = models.IntegerField(null=True)
    backlogs = models.IntegerField(default=0)
    skills = models.TextField(blank=True, help_text="Comma-separated skills (e.g., Python, Django, JavaScript)")
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    is_placed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class CompanyProfile(models.Model):
    """
    Stores all data specific to a company. Linked one-to-one with the User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='company_profile')
    name = models.CharField(max_length=200)
    description = models.TextField(help_text="A brief description of the company.")
    website = models.URLField(blank=True)
    logo = models.FileField(upload_to='company_logos/', null=True, blank=True)
    is_approved = models.BooleanField(default=False, help_text="Admin must approve the company profile.")
    hr_name = models.CharField(max_length=150, blank=True)
    hr_email = models.EmailField(blank=True)

    def __str__(self):
        return self.name

# ==============================================================================
# 3. Core Functional Models
# ==============================================================================
class JobPosting(models.Model):
    """
    Represents a job opening posted by a company.
    """
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    salary_range = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100)
    application_deadline = models.DateField()
    min_cgpa = models.FloatField(default=6.0, help_text="Minimum CGPA required.")
    max_backlogs = models.IntegerField(default=0, help_text="Maximum number of backlogs allowed.")
    allowed_branches = models.CharField(max_length=255, help_text="Comma-separated list of allowed branches (e.g., CSE,ECE,ME).")
    is_approved = models.BooleanField(default=False, help_text="Admin must approve the job posting.")
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company.name}"

class Application(models.Model):
    """
    Links a Student to a JobPosting, representing a single job application.
    """
    STATUS_CHOICES = (
        ('Applied', 'Applied'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
        ('Interview', 'Interview'),
        ('Offered', 'Offered'),
    )
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Applied')

    class Meta:
        # Ensures a student can apply to a specific job only once
        unique_together = ('job', 'student')

    def __str__(self):
        return f"{self.student.user.username}'s application for {self.job.title}"

# ==============================================================================
# 4. Utility & Optional Models
# ==============================================================================
class InterviewSchedule(models.Model):
    """
    Schedules an interview for a specific application.
    """
    
    MODE_CHOICES = (
        ('Online', 'Online'),
        ('In-Person', 'In-Person'),
    )

    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    interview_date = models.DateField()
    interview_time = models.TimeField()
    round_name = models.CharField(max_length=100, help_text="e.g., Technical Round 1, HR Round")
    
    
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='Online')
    
    venue_or_link = models.CharField(max_length=255)
    additional_instructions = models.TextField(blank=True, help_text="Any additional instructions for the candidate.")

class Document(models.Model):
    """
    For admins to upload documents like guidelines, templates, etc.
    """
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    """
    Tracks important actions performed by users in the system.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"