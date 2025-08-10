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