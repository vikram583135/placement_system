# core/decorators.py

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def student_required(function):
    # A decorator that checks if the user is a student
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.role == 'student',
        login_url='login',
        redirect_field_name=None
    )
    return actual_decorator(function)

def company_required(function):
    # A decorator that checks if the user is a company
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.role == 'company',
        login_url='login',
        redirect_field_name=None
    )
    return actual_decorator(function)

def admin_required(function):
    # A decorator that checks if the user is an admin
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.role == 'admin',
        login_url='login',
        redirect_field_name=None
    )
    return actual_decorator(function)

from django.contrib import messages
from django.shortcuts import redirect

def company_approved_required(function):
    # Decorator to ensure only approved companies can post jobs, etc.
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'company':
            if hasattr(request.user, 'company_profile') and request.user.company_profile.is_approved:
                return function(request, *args, **kwargs)
            else:
                messages.error(request, 'Your company profile is pending approval from the placement office.')
                return redirect('core:company_dashboard')
        return redirect('core:login')
    return wrap