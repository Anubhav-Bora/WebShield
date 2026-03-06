"""
WebSocket connection manager for real-time event broadcasting.
"""
import json
import logging
from typing import Set, Dict, Any
from datetime import datetime
from fastapi import WebSocket

logger = logging.getLogger(__name__)

# Maximum concurrent WebSocket connections
MAX_WEBSOCKET_CONNECTIONS = 1000


class WebSocketManager:
    """
    Manages WebSocket connections and broadcasts events to connected clients.
    
    Features:
    - Connection tracking with limits
    - Event broadcasting
    - Graceful disconnection handling
    """
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_count = 0
    
    async def connect(self, websocket: WebSocket):
        """
        Accept a new WebSocket connection.
        
        Raises:
            Exception if max connections exceeded
        """
        # Check connection limit
        if len(self.active_connections) >= MAX_WEBSOCKET_CONNECTIONS:
            await websocket.close(code=1008, reason="Server at max capacity")
            logger.warning(f"WebSocket connection rejected: max connections ({MAX_WEBSOCKET_CONNECTIONS}) reached")
            return
        
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_count += 1
        logger.info(f"✓ WebSocket connected. Total connections: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"✓ WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """
        Broadcast an event to all connected clients.
        
        Args:
            event_type: Type of event (webhook_received, webhook_forwarded, etc.)
            data: Event data to send
        """
        if not self.active_connections:
            return
        
        message = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            await self.disconnect(connection)
    
    async def broadcast_webhook_event(self, webhook_id: str, provider_name: str, status: str):
        """Broadcast a webhook event."""
        await self.broadcast("webhook_event", {
            "webhook_id": webhook_id,
            "provider_name": provider_name,
            "status": status
        })
    
    async def broadcast_stats_update(self, stats: Dict[str, Any]):
        """Broadcast updated webhook statistics."""
        await self.broadcast("stats_update", stats)
    
    async def broadcast_security_event(self, event_type: str, provider_name: str, details: Dict[str, Any]):
        """Broadcast a security event."""
        await self.broadcast("security_event", {
            "event_type": event_type,
            "provider_name": provider_name,
            "details": details
        })
    
    async def broadcast_alert(self, alert_type: str, message: str, severity: str = "warning"):
        """Broadcast an alert to all connected clients."""
        await self.broadcast("alert", {
            "alert_type": alert_type,
            "message": message,
            "severity": severity
        })


# Global WebSocket manager instance
ws_manager = WebSocketManager()
