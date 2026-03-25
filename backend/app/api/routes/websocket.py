"""
WebSocket routes for real-time event streaming.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Query, Depends
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.websocket_manager import ws_manager
from app.core.auth import verify_token
from app.db.session import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(None), db: AsyncSession = Depends(get_db)):
    """
    WebSocket endpoint for real-time event streaming.
    
    Requires authentication via JWT token in query parameter.
    Broadcasts webhook events, security events, and analytics updates.
    """
    logger.info(f"[WEBSOCKET] Connection attempt received")
    
    if not token:
        logger.warning("[WEBSOCKET] Missing authentication token")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing authentication token")
        return
    
    logger.info(f"[WEBSOCKET] Token received: {token[:20]}..." if len(token) > 20 else f"[WEBSOCKET] Token received: {token}")
    
    try:
        user = await verify_token(token, db)
        if not user:
            logger.warning("[WEBSOCKET] Invalid token - user not found")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication token")
            return
        
        logger.info(f"[WEBSOCKET] Token verified for user: {user.username}")
    except Exception as e:
        logger.error(f"[WEBSOCKET] Authentication failed with exception: {type(e).__name__}: {str(e)}", exc_info=True)
        try:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
        except Exception as close_err:
            logger.error(f"[WEBSOCKET] Error closing connection: {str(close_err)}")
        return
    
    try:
        # Accept the WebSocket connection first
        try:
            logger.info(f"[WEBSOCKET] Accepting connection for user: {user.username}")
            await websocket.accept()
            logger.info(f"[WEBSOCKET] Connection accepted successfully for user: {user.username}")
        except Exception as accept_err:
            logger.error(f"[WEBSOCKET] Failed to accept connection: {type(accept_err).__name__}: {str(accept_err)}", exc_info=True)
            return
        
        try:
            await ws_manager.connect(websocket, str(user.id))
            logger.info(f"[WEBSOCKET] User registered in connection manager. Total connections: {len(ws_manager.active_connections)}")
        except Exception as manager_err:
            logger.error(f"[WEBSOCKET] Failed to register in connection manager: {type(manager_err).__name__}: {str(manager_err)}", exc_info=True)
            await websocket.close(code=status.WS_1011_SERVER_ERROR)
            return
        
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
        logger.error(f"[WEBSOCKET] WebSocket connection error: {type(e).__name__}: {str(e)}", exc_info=True)
        try:
            # Use integer code 1011 for server error instead of non-existent constant
            await websocket.close(code=1011, reason="Server error")
        except Exception:
            logger.debug("[WEBSOCKET] Could not close connection")
        if 'user' in locals():
            await ws_manager.disconnect(websocket, str(user.id))
        else:
            await ws_manager.disconnect(websocket, None)
