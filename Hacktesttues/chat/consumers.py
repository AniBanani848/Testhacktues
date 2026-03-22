import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.friendship_id = int(self.scope['url_route']['kwargs']['friendship_id'])
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close(code=4401)
            return

        allowed = await sync_to_async(self._user_allowed_in_friendship)()
        if not allowed:
            await self.close(code=4403)
            return

        self.room_group_name = f'chat_{self.friendship_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    def _user_allowed_in_friendship(self):
        from .models import Friendship

        try:
            fs = Friendship.objects.get(pk=self.friendship_id, status=Friendship.Status.ACCEPTED)
        except Friendship.DoesNotExist:
            return False
        return self.user in (fs.from_user, fs.to_user)

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data or '{}')
        except json.JSONDecodeError:
            return
        body = (data.get('message') or '').strip()
        if not body:
            return
        body = body[:2000]

        payload = await sync_to_async(self._persist_and_payload)(body)
        if not payload:
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'relay', 'payload': payload},
        )

    def _persist_and_payload(self, body):
        from .models import ChatMessage, Friendship

        try:
            fs = Friendship.objects.get(pk=self.friendship_id, status=Friendship.Status.ACCEPTED)
        except Friendship.DoesNotExist:
            return None
        if self.user not in (fs.from_user, fs.to_user):
            return None

        msg = ChatMessage.objects.create(friendship=fs, sender=self.user, body=body)
        return {
            'type': 'message',
            'id': msg.id,
            'body': msg.body,
            'sender_id': msg.sender_id,
            'username': msg.sender.username,
            'created_at': timezone.localtime(msg.created_at).isoformat(),
        }

    async def relay(self, event):
        await self.send(text_data=json.dumps(event['payload']))
