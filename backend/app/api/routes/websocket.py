"""
WebSocket routes for real-time event streaming.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Query
import logging
from datetime import datetime

from app.core.websocket_manager import ws_manager
from app.core.auth import verify_token

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(None)):
    """
    WebSocket endpoint for real-time event streaming.
    
    Requires authentication via JWT token in query parameter.
    Broadcasts webhook events, security events, and analytics updates.
    """
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing authentication token")
        return
    
    try:
        user = await verify_token(token)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication token")
            return
    except Exception as e:
        logger.warning(f"WebSocket authentication failed: {str(e)}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
        return
    
    try:
        await ws_manager.connect(websocket, str(user.id))
        
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "data": {
                "status": "connected",
                "message": "WebSocket connected successfully",
                "user": user.username,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                # Echo back for testing
                await websocket.send_json({
                    "type": "echo",
                    "data": {"message": data},
                    "timestamp": datetime.utcnow().isoformat()
                })
            except WebSocketDisconnect:
                await ws_manager.disconnect(websocket, str(user.id))
                logger.info(f"Client disconnected. Total connections: {len(ws_manager.active_connections)}")
                break
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                await ws_manager.disconnect(websocket, str(user.id))
                break
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        try:
            await websocket.close(code=status.WS_1011_SERVER_ERROR)
        except Exception:
            pass
        await ws_manager.disconnect(websocket, str(user.id) if 'user' in locals() else None)
