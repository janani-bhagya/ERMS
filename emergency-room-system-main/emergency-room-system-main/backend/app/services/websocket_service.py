# backend/app/services/websocket_service.py
import socketio
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class WebSocketService:
    def __init__(self):
        self.sio = socketio.AsyncServer(
            async_mode='asgi',
            cors_allowed_origins=['http://localhost:3000', 'http://localhost:8000'],
            logger=True,
            engineio_logger=True
        )
        self.connected_clients: Dict[str, str] = {}
        self.setup_handlers()

    def setup_handlers(self):
        @self.sio.event
        async def connect(sid, environ):
            logger.info(f"Client connected: {sid}")
            self.connected_clients[sid] = sid
            await self.sio.emit('connection_status', {'status': 'connected', 'sid': sid}, room=sid)

        @self.sio.event
        async def disconnect(sid):
            logger.info(f"Client disconnected: {sid}")
            if sid in self.connected_clients:
                del self.connected_clients[sid]

        @self.sio.event
        async def subscribe(sid, data):
            """Subscribe client to specific data channels"""
            channel = data.get('channel', 'general')
            await self.sio.enter_room(sid, channel)
            logger.info(f"Client {sid} subscribed to {channel}")
            await self.sio.emit('subscribed', {'channel': channel}, room=sid)

    async def broadcast_patient_update(self, patient_data: Dict[str, Any]):
        """Broadcast patient updates to all connected clients"""
        await self.sio.emit('patient_update', patient_data)
        logger.info(f"Broadcasted patient update: {patient_data.get('id')}")

    async def broadcast_triage_update(self, triage_data: Dict[str, Any]):
        """Broadcast triage queue updates"""
        await self.sio.emit('triage_update', triage_data)
        logger.info(f"Broadcasted triage update")

    async def broadcast_resource_update(self, resource_data: Dict[str, Any]):
        """Broadcast resource allocation updates"""
        await self.sio.emit('resource_update', resource_data)
        logger.info(f"Broadcasted resource update: {resource_data.get('id')}")

    async def broadcast_metrics(self, metrics: Dict[str, Any]):
        """Broadcast real-time metrics"""
        await self.sio.emit('metrics_update', metrics)

    async def notify_patient_status(self, patient_id: str, status: str):
        """Send patient status notification"""
        await self.sio.emit('patient_status', {
            'patient_id': patient_id,
            'status': status
        })

    def get_asgi_app(self):
        """Get the ASGI app for mounting"""
        return socketio.ASGIApp(self.sio)

# Global instance
websocket_service = WebSocketService()
