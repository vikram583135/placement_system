# core/forms.py

from django import forms
# Correctly import OUR custom User model and other models from this app
from .models import User, StudentProfile, CompanyProfile, JobPosting, InterviewSchedule

# ==============================================================================
# 1. Registration Forms
# ==============================================================================

class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User # This now correctly refers to our custom User model
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            StudentProfile.objects.create(user=user)
        return user


class CompanyRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    company_name = forms.CharField(max_length=200, label="Company Name")

    class Meta:
        model = User # This now correctly refers to our custom User model
        fields = ['username', 'email']

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'company'
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            CompanyProfile.objects.create(
                user=user,
                name=self.cleaned_data['company_name']
            )
        return user

# ==============================================================================
# 2. Profile & Update Forms
# ==============================================================================

class UserUpdateForm(forms.ModelForm):
    """Form for updating basic user information like name and email."""
    email = forms.EmailField()

    class Meta:
        model = User # This now correctly refers to our custom User model
        fields = ['first_name', 'last_name', 'email']

class StudentProfileForm(forms.ModelForm):
    """Form for updating the student-specific profile data."""
    class Meta:
        model = StudentProfile
        exclude = ['user', 'is_placed']
        widgets = {
            'branch': forms.TextInput(attrs={'placeholder': 'e.g., Computer Science Engineering'}),
            'cgpa': forms.NumberInput(attrs={'placeholder': 'e.g., 8.75'}),
            'backlogs': forms.NumberInput(attrs={'placeholder': 'e.g., 0'}),
            'skills': forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g., Python, Django, React, SQL'}),
            'linkedin_url': forms.URLInput(attrs={'placeholder': 'https://www.linkedin.com/in/yourprofile'}),
            'github_url': forms.URLInput(attrs={'placeholder': 'https://github.com/yourusername'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'e.g., +919876543210'}),
        }

# --- CORRECTED: This form is now properly de-indented ---
class CompanyProfileForm(forms.ModelForm):
    """Form for updating the company-specific profile data."""
    class Meta:
        model = CompanyProfile
        exclude = ['user', 'is_approved']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your official company name'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://www.yourcompany.com'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'A brief description of your company, mission, and culture.'}),
        }

# ==============================================================================
# 3. Core Functional Forms
# ==============================================================================

class JobPostingForm(forms.ModelForm):
    """
    Form for companies to create and edit job postings.
    """
    application_deadline = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="The last day for students to apply."
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text="A detailed description of the job role and responsibilities."
    )
    allowed_branches = forms.CharField(
        help_text="Enter comma-separated branch codes (e.g., CSE, ECE, ME)."
    )

    class Meta:
        model = JobPosting
        # The 'company' and 'is_approved' fields will be set automatically in the view
        exclude = ['company', 'is_approved', 'posted_at']

# ==============================================================================
# 4. Utility Forms
# ==============================================================================

class BulkUploadForm(forms.Form):
    UPLOAD_TYPE_CHOICES = (
        ('students', 'Students'),
        ('companies', 'Companies'),
    )
    upload_type = forms.ChoiceField(
        choices=UPLOAD_TYPE_CHOICES,
        label="Select Data Type to Upload",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    csv_file = forms.FileField(
        label="Upload CSV File",
        help_text="Please use the provided templates."
    )

class ResumeUploadForm(forms.ModelForm):
    """A simple form to handle resume file uploads."""
    class Meta:
        model = StudentProfile
        # We only want the resume field in this form
        fields = ['resume']
        labels = {
            'resume': 'Upload Your Resume File (PDF or DOCX)',
        }

class InterviewScheduleForm(forms.ModelForm):
    """
    A form for scheduling an interview for shortlisted candidates.
    """
    interview_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    interview_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    
    class Meta:
        model = InterviewSchedule
        # The application is linked in the view, not selected in the form.
        fields = ['interview_date', 'interview_time', 'round_name', 'venue_or_link']

class InterviewScheduleForm(forms.ModelForm):
    """
    A form for scheduling an interview for shortlisted candidates.
    """
    # Use widgets to get user-friendly date and time inputs in the browser
    interview_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    interview_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    
    class Meta:
        model = InterviewSchedule
        # The 'application' is linked automatically in the view, not selected in the form.
        fields = ['interview_date', 'interview_time', 'round_name', 'mode', 'venue_or_link', 'additional_instructions']
        labels = {
            'round_name': 'Interview Round Name (e.g., Technical Round 1)',
            'venue_or_link': 'Venue or Meeting Link (e.g., Google Meet URL)',
        }