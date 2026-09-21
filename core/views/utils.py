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
def notifications_view(request):
    """
    Displays a list of notifications for the logged-in user.
    """
    from core.models import Notification

    # Handle "mark as read" action
    if request.method == 'POST' and request.POST.get('action') == 'mark_read':
        notif_id = request.POST.get('notification_id')
        if notif_id:
            try:
                notif = Notification.objects.get(id=notif_id, user=request.user)
                notif.is_read = True
                notif.save()
            except Notification.DoesNotExist:
                pass
        return redirect('core:notifications')

    # Handle "mark all as read" action
    if request.method == 'POST' and request.POST.get('action') == 'mark_all_read':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return redirect('core:notifications')

    notifications = Notification.objects.filter(user=request.user)
    context = {'notifications': notifications}
    return render(request, 'notifications.html', context)


@login_required
def chat_view(request):
    return render(request, 'chat.html')


@login_required
@admin_required
def document_upload_view(request):
    """Handles uploading and listing documents."""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        uploaded_file = request.FILES.get('file')
        if title and uploaded_file:
            Document.objects.create(title=title, file=uploaded_file)
            messages.success(request, f'Document "{title}" uploaded successfully.')
            return redirect('core:document_upload')
        else:
            messages.error(request, 'Please provide both a title and a file.')
    
    documents = Document.objects.all().order_by('-uploaded_at')
    return render(request, 'admin/document_upload.html', {'documents': documents})


@login_required
@admin_required
@require_POST
def delete_document_view(request, doc_id):
    """Deletes a document by ID."""
    document = get_object_or_404(Document, id=doc_id)
    doc_title = document.title
    # Delete the physical file from storage
    if document.file:
        document.file.delete(save=False)
    document.delete()
    messages.success(request, f'Document "{doc_title}" has been deleted.')
    return redirect('core:document_upload')


@login_required
def view_resume_view(request, student_id):
    """Serves a student's resume file for viewing/download."""
    student_profile = get_object_or_404(StudentProfile, user_id=student_id)
    
    if not student_profile.resume:
        messages.error(request, 'This student has not uploaded a resume.')
        raise Http404('Resume not found.')
    
    # Serve the file inline (opens in browser for PDFs)
    try:
        return FileResponse(
            student_profile.resume.open('rb'),
            content_type='application/pdf',
            as_attachment=False,
            filename=f"{student_profile.user.get_full_name()}_resume.pdf"
        )
    except FileNotFoundError:
        raise Http404('Resume file not found on server.')


