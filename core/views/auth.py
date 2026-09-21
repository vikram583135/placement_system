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
    messages.info(request, "You have been logged out.")
    return redirect('core:home')


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep user logged in
            messages.success(request, 'Your password was successfully updated!')
            # Redirect back to their dashboard depending on role
            if user.role == 'student':
                return redirect('core:student_dashboard')
            elif user.role == 'company':
                return redirect('core:company_dashboard')
            else:
                return redirect('core:admin_dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeCustomForm(request.user)
    return render(request, 'auth/password_change.html', {'form': form})


