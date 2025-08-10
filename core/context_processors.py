
# core/context_processors.py

from .models import JobPosting

def notifications_context(request):
    """
    Makes a notification count available to all templates.
    """
    if request.user.is_authenticated and request.user.role == 'admin':
        # Calculate the count only for logged-in admins
        count = JobPosting.objects.filter(is_approved=False).count()
        return {'pending_jobs_count': count}
    
    # Return an empty dictionary for other users
    return {}