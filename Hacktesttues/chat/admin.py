from django.contrib import admin

from .models import ChatMessage, Friendship


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('friendship_id', 'sender', 'body_preview', 'created_at')
    search_fields = ('body', 'sender__username')

    @admin.display(description='Body')
    def body_preview(self, obj):
        return (obj.body[:60] + '…') if len(obj.body) > 60 else obj.body
