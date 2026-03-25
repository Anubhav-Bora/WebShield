"""
WebSocket connection manager for broadcasting real-time events.
"""
from fastapi import WebSocket
import logging
from typing import List, Dict, Any
import json

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasts events to connected clients."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)
        
        logger.info(f"WebSocket connected for user {user_id}. Total: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket, user_id: str = None):
        """Unregister a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to all connections of a specific user."""
        if user_id in self.user_connections:
            disconnected = []
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message: {e}")
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                await self.disconnect(conn, user_id)
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Send message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)


# Global WebSocket manager instance
ws_manager = WebSocketManager()
