import secrets
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

CODE_LENGTH = 6
CODE_TTL = timedelta(minutes=30)
RESEND_COOLDOWN = timedelta(seconds=60)


def generate_code():
    return ''.join(secrets.choice('0123456789') for _ in range(CODE_LENGTH))


def assign_new_code(profile):
    profile.email_verification_code = generate_code()
    profile.email_verification_sent_at = timezone.now()
    profile.save(update_fields=['email_verification_code', 'email_verification_sent_at'])
    return profile.email_verification_code


def send_verification_email(user):
    """Generate a fresh code and email it to the user."""
    if not user.email:
        return False
    code = assign_new_code(user.profile)
    subject = 'Your StudyLink verification code'
    body = (
        f'Hi {user.username},\n\n'
        f'Your verification code is: {code}\n\n'
        f'It expires in {int(CODE_TTL.total_seconds() // 60)} minutes.\n\n'
        'If you did not sign up for StudyLink, you can ignore this email.\n'
    )
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=not settings.DEBUG,
    )
    return True


def code_is_valid(profile, entered: str) -> bool:
    if profile.email_verified:
        return True
    code = (entered or '').strip()
    if len(code) != CODE_LENGTH or not code.isdigit():
        return False
    if not profile.email_verification_code:
        return False
    if code != profile.email_verification_code:
        return False
    sent = profile.email_verification_sent_at
    if not sent:
        return False
    if timezone.now() - sent > CODE_TTL:
        return False
    return True


def can_resend(profile) -> bool:
    sent = profile.email_verification_sent_at
    if not sent:
        return True
    return timezone.now() - sent >= RESEND_COOLDOWN


def mark_verified(profile):
    profile.email_verified = True
    profile.email_verification_code = ''
    profile.email_verification_sent_at = None
    profile.save(update_fields=['email_verified', 'email_verification_code', 'email_verification_sent_at'])
