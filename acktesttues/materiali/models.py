from django.db import models
from django.contrib.auth.models import User
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # What the user is learning (e.g., "Computer Science", "Biology")
    current_major = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    # Optional: A profile picture
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

class Resource(models.Model):
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    # The actual file (PDF, Image, etc.)
    file = models.FileField(upload_to='resources/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    course_code = models.CharField(max_length=20, blank=True)  # Optional: Course code (e.g., "CS101")
    def save(self, *args, **kwargs):
        # Automatically make the course code uppercase before saving
        self.course_code = self.course_code.upper()
        super().save(*args, **kwargs)


class Supply(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100)
    description = models.TextField()
    is_available = models.BooleanField(default=True)


