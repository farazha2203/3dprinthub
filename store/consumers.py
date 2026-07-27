from __future__ import annotations

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .realtime import analysis_group, operations_group, user_notification_group


class RealtimeConsumer(AsyncJsonWebsocketConsumer):
    async def realtime_message(self, event):
        await self.send_json({"event": event.get("event"), "payload": event.get("payload", {})})


class CustomerNotificationConsumer(RealtimeConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return
        self.group_name = user_notification_group(user.pk)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json({"event": "notification.initial", "payload": await self.initial_payload(user.pk)})

    async def disconnect(self, close_code):
        if getattr(self, "group_name", None):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    @database_sync_to_async
    def initial_payload(self, user_id):
        from .models import CustomerNotification
        return {"unread_count": CustomerNotification.objects.filter(user_id=user_id, read_at__isnull=True).count()}


class LinkAnalysisProgressConsumer(RealtimeConsumer):
    async def connect(self):
        token = self.scope["url_route"]["kwargs"]["token"]
        access = await self.access_payload(token)
        if access is None:
            await self.close(code=4403)
            return
        self.group_name = analysis_group(token)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json({"event": "link.job", "payload": access})

    async def disconnect(self, close_code):
        if getattr(self, "group_name", None):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    @database_sync_to_async
    def access_payload(self, token):
        from .realtime import job_realtime_payload
        from .models import CustomerLinkAnalysis

        analysis = CustomerLinkAnalysis.objects.select_related("job").filter(public_token=token).first()
        if analysis is None:
            return None
        user = self.scope.get("user")
        if analysis.user_id:
            if not user or not user.is_authenticated or user.pk != analysis.user_id:
                return None
        else:
            session = self.scope.get("session")
            session_key = getattr(session, "session_key", "") if session is not None else ""
            if not session_key or session_key != analysis.session_key:
                return None
        if hasattr(analysis, "job"):
            return job_realtime_payload(analysis.job.pk)
        return {"status": analysis.status, "job_status": "missing", "is_terminal": analysis.status in {"ready", "partial", "needs_input", "failed", "converted"}}


class AdminLinkOperationsConsumer(RealtimeConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated or not user.is_staff:
            await self.close(code=4403)
            return
        self.group_name = operations_group()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json({"event": "operations.snapshot", "payload": await self.snapshot()})

    async def disconnect(self, close_code):
        if getattr(self, "group_name", None):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    @database_sync_to_async
    def snapshot(self):
        from .realtime import operations_snapshot
        return operations_snapshot()
