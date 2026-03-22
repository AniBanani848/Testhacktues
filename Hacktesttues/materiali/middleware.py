from django.shortcuts import redirect
from django.urls import resolve

from .models import Profile


class RequireEmailVerifiedMiddleware:
    """Send logged-in users without a verified email to the verification page."""

    EXEMPT_URL_NAMES = frozenset(
        {
            'verify_email',
            'resend_verification',
            'logout',
            'login',
            'register',
        },
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        if path.startswith('/static/') or path.startswith('/media/'):
            return self.get_response(request)
        if path.startswith('/admin') and getattr(request.user, 'is_staff', False):
            return self.get_response(request)

        if request.user.is_authenticated:
            try:
                verified = Profile.objects.get(user_id=request.user.pk).email_verified
            except Profile.DoesNotExist:
                verified = True
            if not verified:
                try:
                    name = resolve(path).url_name
                except Exception:
                    name = None
                if name not in self.EXEMPT_URL_NAMES:
                    return redirect('verify_email')

        return self.get_response(request)
