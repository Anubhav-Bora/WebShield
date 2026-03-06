"""
WebSocket routes for real-time event streaming.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Query
import logging
import asyncio

from app.core.websocket_manager import ws_manager
from app.core.auth import verify_token

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(None)):
    """
    WebSocket endpoint for real-time event streaming.
    
    Requires authentication via JWT token in query parameter.
    Note: Token is passed as query parameter because browsers don't support custom headers in WebSocket.
    In production, use secure WebSocket (wss://) to encrypt the token in transit.
    
    Clients connect here to receive live updates about:
    - Webhook events (received, forwarded, failed)
    - Security events
    - Statistics updates
    - Alerts
    """
    # Verify token before accepting connection
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing authentication token")
        return
    
    try:
        # Verify JWT token
        user = await verify_token(token)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication token")
            return
    except Exception as e:
        logger.warning(f"WebSocket authentication failed: {str(e)}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
        return
    
    try:
        await ws_manager.connect(websocket)
        logger.info(f"✓ WebSocket client connected (user: {user.username}). Total connections: {len(ws_manager.active_connections)}")
        
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "data": {"status": "connected", "message": "WebSocket connected successfully", "user": user.username},
            "timestamp": asyncio.get_event_loop().time()
        })
        
        while True:
            # Keep connection alive and listen for client messages
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received message from client: {data}")
                
                # Echo back for testing
                await websocket.send_json({
                    "type": "echo",
                    "data": {"message": data},
                    "timestamp": asyncio.get_event_loop().time()
                })
            except WebSocketDisconnect:
                await ws_manager.disconnect(websocket)
                logger.info(f"✓ Client disconnected. Total connections: {len(ws_manager.active_connections)}")
                break
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                await ws_manager.disconnect(websocket)
                break
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        try:
            await websocket.close(code=status.WS_1011_SERVER_ERROR)
        except Exception:
            pass
        await ws_manager.disconnect(websocket)
