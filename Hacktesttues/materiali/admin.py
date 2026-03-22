from django.contrib import admin

from .models import Profile, Resource, Supply


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_verified', 'current_major', 'learning_focus')
    list_filter = ('email_verified',)
    search_fields = ('user__username', 'current_major', 'learning_focus')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'course_code', 'uploader', 'uploaded_at')
    list_filter = ('subject',)
    search_fields = ('title', 'course_code', 'uploader__username')


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'subject_area', 'owner', 'is_available')
    list_filter = ('is_available', 'subject_area')
