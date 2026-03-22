from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    current_major = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='What you study (e.g. Computer Science, Biology).',
    )
    learning_focus = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text='Optional: course, topic, or semester focus.',
    )
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if kwargs.get('raw'):
        return
    if created:
        Profile.objects.get_or_create(
            user=instance,
            defaults={'current_major': '', 'learning_focus': ''},
        )
    else:
        try:
            instance.profile.save()
        except Profile.DoesNotExist:
            Profile.objects.create(user=instance, current_major='', learning_focus='')


class Resource(models.Model):
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    subject = models.CharField(
        max_length=100,
        help_text='Subject or field this material belongs to (often matches what you study).',
    )
    file = models.FileField(upload_to='resources/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    course_code = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):
        if self.course_code:
            self.course_code = self.course_code.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Supply(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supplies')
    item_name = models.CharField(max_length=100)
    description = models.TextField()
    subject_area = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='Study area for this item so peers in the same field can find it.',
    )
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.item_name
