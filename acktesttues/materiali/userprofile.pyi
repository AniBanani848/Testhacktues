from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True, verbose_name="Биография")
    current_learning = models.CharField(max_length=255, blank=True, null=True, verbose_name="Какво учи в момента")
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, verbose_name="Снимка на профила")

    def __str__(self):
        return self.user.username

class Resource(models.Model):
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Качил")
    title = models.CharField(max_length=255, verbose_name="Заглавие")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    file = models.FileField(upload_to='resources/', verbose_name="Файл")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата на качване")

    def __str__(self):
        return self.title

class ExchangeItem(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Собственик")
    name = models.CharField(max_length=255, verbose_name="Име на предмета")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    available = models.BooleanField(default=True, verbose_name="Наличен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата на добавяне")
    
    def __str__(self):
        статус = "Наличен" if self.available else "Не е наличен"
        return f"{self.name} ({статус})"