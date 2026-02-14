"""WebSocket consumers for real-time updates."""
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.utils import timezone


class NotificationConsumer(AsyncWebsocketConsumer):
    """Consumer for real-time notifications."""

    async def connect(self):
        """Handle WebSocket connection."""
        if self.scope["user"].is_authenticated:
            self.group_name = f'user_{self.scope["user"].id}'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Connected to real-time updates'
            }))
        else:
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if self.scope["user"].is_authenticated:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle incoming messages."""
        try:
            data = json.loads(text_data)
            event_type = data.get('type')

            if event_type == 'get_updates':
                await self.send_updates()
        except json.JSONDecodeError:
            pass

    async def send_updates(self):
        """Send current user updates."""
        user = self.scope["user"]
        borrowings = await self.get_active_borrowings(user)
        overdue_count = await self.count_overdue(user)

        await self.send(text_data=json.dumps({
            'type': 'updates',
            'active_borrowings': len(borrowings),
            'overdue_count': overdue_count,
            'timestamp': timezone.now().isoformat()
        }))

    async def notification_message(self, event):
        """Handle notification message."""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'title': event['title'],
            'message': event['message'],
            'notification_type': event['notification_type']
        }))

    @database_sync_to_async
    def get_active_borrowings(self, user):
        """Get user's active borrowings."""
        return list(user.borrowings.filter(returned_at__isnull=True))

    @database_sync_to_async
    def count_overdue(self, user):
        """Count overdue borrowings."""
        borrowings = user.borrowings.filter(returned_at__isnull=True)
        return sum(1 for b in borrowings if b.is_overdue())
