"""
Security Simulation Engine for WebShield.

This module generates and executes various attack simulations to demonstrate
WebShield's security capabilities. It includes:
- Attack generators for different vulnerability types
- Simulation execution with response capture
- Result analysis and educational insights
"""
import json
import hmac
import hashlib
import httpx
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AttackType(str, Enum):
    """Types of attacks that can be simulated."""
    INVALID_SIGNATURE = "invalid_signature"
    REPLAY_ATTACK = "replay_attack"
    TAMPERED_PAYLOAD = "tampered_payload"
    RATE_LIMIT = "rate_limit"
    OLD_TIMESTAMP = "old_timestamp"
    FUTURE_TIMESTAMP = "future_timestamp"
    MISSING_SIGNATURE = "missing_signature"
    MALFORMED_JSON = "malformed_json"
    OVERSIZED_PAYLOAD = "oversized_payload"


class AttackGenerator:
    """Generate various attack payloads to test security measures."""
    
    @staticmethod
    def generate_invalid_signature_attack(
        provider_secret: str,
        payload: Dict[str, Any]
    ) -> Tuple[str, Dict[str, str]]:
        """
        Generate webhook with intentionally invalid signature.
        
        Returns:
            Tuple of (payload_str, headers)
        """
        payload_str = json.dumps(payload)
        
        # Create WRONG signature (intentionally invalid)
        wrong_signature = hmac.new(
            b"wrong_secret_key",
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            "X-Webhook-Signature": wrong_signature,
            "Content-Type": "application/json"
        }
        
        return payload_str, headers
    
    @staticmethod
    def generate_tampered_payload_attack(
        provider_secret: str,
        original_payload: Dict[str, Any]
    ) -> Tuple[str, Dict[str, str]]:
        """
        Generate webhook with tampered payload but valid signature.
        
        Original signature is valid, but payload is modified.
        This tests payload integrity checking.
        """
        # Create signature for original payload
        original_str = json.dumps(original_payload)
        signature = hmac.new(
            provider_secret.encode(),
            original_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Modify the payload
        tampered_payload = original_payload.copy()
        if isinstance(tampered_payload.get("data"), dict):
            tampered_payload["data"]["amount"] = 999999  # Tamper with data
        elif isinstance(tampered_payload.get("amount"), (int, float)):
            tampered_payload["amount"] = 999999
        else:
            tampered_payload["tampered"] = True
        
        tampered_str = json.dumps(tampered_payload)
        
        headers = {
            "X-Webhook-Signature": signature,  # Valid signature for ORIGINAL payload
            "Content-Type": "application/json"
        }
        
        # Return tampered payload with signature of original
        return tampered_str, headers
    
    @staticmethod
    def generate_replay_attack(
        provider_secret: str,
        payload: Dict[str, Any],
        request_id: str
    ) -> Tuple[str, Dict[str, str]]:
        """
        Generate exact duplicate webhook (same request_id).
        
        This tests replay attack protection.
        """
        payload_str = json.dumps(payload)
        signature = hmac.new(
            provider_secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            "X-Webhook-Signature": signature,
            "X-Request-ID": request_id,  # Same as previous
            "Content-Type": "application/json"
        }
        
        return payload_str, headers
    
    @staticmethod
    def generate_missing_signature_attack(
        payload: Dict[str, Any]
    ) -> Tuple[str, Dict[str, str]]:
        """
        Generate webhook without signature header.
        
        Tests authentication requirement.
        """
        payload_str = json.dumps(payload)
        
        headers = {
            # NO X-Webhook-Signature header
            "Content-Type": "application/json"
        }
        
        return payload_str, headers
    
    @staticmethod
    def generate_old_timestamp_attack(
        provider_secret: str,
        base_payload: Dict[str, Any]
    ) -> Tuple[str, Dict[str, str]]:
        """
        Generate webhook with timestamp > 5 minutes old.
        
        Tests timestamp validation (prevents old requests).
        """
        # Create payload with old timestamp (10 minutes ago)
        old_time = (datetime.utcnow() - timedelta(minutes=10)).isoformat() + "Z"
        payload = base_payload.copy()
        payload["timestamp"] = old_time
        
        payload_str = json.dumps(payload)
        signature = hmac.new(
            provider_secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            "X-Webhook-Signature": signature,
            "X-Timestamp": old_time,
            "Content-Type": "application/json"
        }
        
        return payload_str, headers
    
    @staticmethod
    def generate_future_timestamp_attack(
        provider_secret: str,
        base_payload: Dict[str, Any]
    ) -> Tuple[str, Dict[str, str]]:
        """
        Generate webhook with future timestamp.
        
        Tests timestamp validation (prevents future requests/clock skew attacks).
        """
        # Create payload with future timestamp (10 minutes in future)
        future_time = (datetime.utcnow() + timedelta(minutes=10)).isoformat() + "Z"
        payload = base_payload.copy()
        payload["timestamp"] = future_time
        
        payload_str = json.dumps(payload)
        signature = hmac.new(
            provider_secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            "X-Webhook-Signature": signature,
            "X-Timestamp": future_time,
            "Content-Type": "application/json"
        }
        
        return payload_str, headers
    
    @staticmethod
    def generate_malformed_json_attack() -> Tuple[str, Dict[str, str]]:
        """
        Generate request with malformed JSON.
        
        Tests JSON parsing validation.
        """
        payload_str = '{"invalid": json without quotes}'  # Invalid JSON
        
        headers = {
            "X-Webhook-Signature": "somesignature",
            "Content-Type": "application/json"
        }
        
        return payload_str, headers
    
    @staticmethod
    def generate_oversized_payload_attack(
        provider_secret: str,
        max_size_kb: int = 1024
    ) -> Tuple[str, Dict[str, str]]:
        """
        Generate oversized payload (exceeds max size limit).
        
        Tests payload size validation.
        """
        # Create payload larger than limit
        large_data = "x" * ((max_size_kb + 10) * 1024)
        payload = {
            "event_type": "test",
            "data": large_data
        }
        
        payload_str = json.dumps(payload)
        signature = hmac.new(
            provider_secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            "X-Webhook-Signature": signature,
            "Content-Type": "application/json"
        }
        
        return payload_str, headers


class SimulationExecutor:
    """Execute attack simulations and capture responses."""
    
    @staticmethod
    async def execute_attack(
        webhook_url: str,
        attack_type: AttackType,
        provider_secret: str,
        base_payload: Dict[str, Any],
        request_id: Optional[str] = None,
        timeout: float = 5.0
    ) -> Dict[str, Any]:
        """
        Execute a single attack and capture the response.
        
        Args:
            webhook_url: Target webhook endpoint
            attack_type: Type of attack to simulate
            provider_secret: Provider's secret key
            base_payload: Base payload to use for attack
            request_id: Optional request ID for replay attacks
            timeout: Request timeout in seconds
        
        Returns:
            Dictionary with attack results
        """
        generator = AttackGenerator()
        
        try:
            # Generate attack payload and headers
            if attack_type == AttackType.INVALID_SIGNATURE:
                payload_str, headers = generator.generate_invalid_signature_attack(
                    provider_secret, base_payload
                )
            elif attack_type == AttackType.TAMPERED_PAYLOAD:
                payload_str, headers = generator.generate_tampered_payload_attack(
                    provider_secret, base_payload
                )
            elif attack_type == AttackType.REPLAY_ATTACK:
                if not request_id:
                    request_id = str(uuid.uuid4())
                payload_str, headers = generator.generate_replay_attack(
                    provider_secret, base_payload, request_id
                )
            elif attack_type == AttackType.MISSING_SIGNATURE:
                payload_str, headers = generator.generate_missing_signature_attack(
                    base_payload
                )
            elif attack_type == AttackType.OLD_TIMESTAMP:
                payload_str, headers = generator.generate_old_timestamp_attack(
                    provider_secret, base_payload
                )
            elif attack_type == AttackType.FUTURE_TIMESTAMP:
                payload_str, headers = generator.generate_future_timestamp_attack(
                    provider_secret, base_payload
                )
            elif attack_type == AttackType.MALFORMED_JSON:
                payload_str, headers = generator.generate_malformed_json_attack()
            elif attack_type == AttackType.OVERSIZED_PAYLOAD:
                payload_str, headers = generator.generate_oversized_payload_attack(
                    provider_secret
                )
            else:
                raise ValueError(f"Unknown attack type: {attack_type}")
            
            # Add request ID if not present
            if "X-Request-ID" not in headers:
                headers["X-Request-ID"] = str(uuid.uuid4())
            
            # Execute attack
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    webhook_url,
                    content=payload_str,
                    headers=headers
                )
            
            return {
                "success": True,
                "status_code": response.status_code,
                "response_body": response.text,
                "headers_sent": dict(headers),
                "was_blocked": response.status_code >= 400,
                "error_type": None
            }
        
        except httpx.TimeoutException:
            logger.error(f"Timeout executing attack {attack_type} to {webhook_url}")
            return {
                "success": False,
                "status_code": 408,
                "response_body": "Request timeout",
                "error": "timeout",
                "error_type": "timeout",
                "was_blocked": False
            }
        except httpx.ConnectError as e:
            logger.error(f"Connection error executing attack {attack_type}: {e}")
            return {
                "success": False,
                "status_code": None,
                "response_body": f"Connection failed: {str(e)}",
                "error": "connection_error",
                "error_type": "connection_error",
                "was_blocked": False
            }
        except Exception as e:
            logger.error(f"Error executing attack {attack_type}: {e}")
            return {
                "success": False,
                "status_code": None,
                "response_body": str(e),
                "error": str(type(e).__name__),
                "error_type": "execution_error",
                "was_blocked": False
            }
    
    @staticmethod
    async def execute_rate_limit_attack(
        webhook_url: str,
        provider_secret: str,
        base_payload: Dict[str, Any],
        num_requests: int = 150,
        concurrent: bool = False
    ) -> Dict[str, Any]:
        """
        Execute rate limit attack by sending many requests rapidly.
        
        Returns statistics about which requests were blocked.
        """
        import asyncio
        
        results = {
            "total_requests": num_requests,
            "successful": 0,
            "blocked": 0,
            "responses": [],
            "rate_limit_triggered_at": None
        }
        
        payload_str = json.dumps(base_payload)
        
        async def send_request(index: int):
            signature = hmac.new(
                provider_secret.encode(),
                payload_str.encode(),
                hashlib.sha256
            ).hexdigest()
            
            headers = {
                "X-Webhook-Signature": signature,
                "X-Request-ID": str(uuid.uuid4()),  # Unique for each request
                "Content-Type": "application/json"
            }
            
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.post(
                        webhook_url,
                        content=payload_str,
                        headers=headers
                    )
                
                was_blocked = response.status_code >= 400
                
                if was_blocked and not results["rate_limit_triggered_at"]:
                    results["rate_limit_triggered_at"] = index
                
                return {
                    "request_num": index,
                    "status_code": response.status_code,
                    "was_blocked": was_blocked
                }
            except Exception as e:
                return {
                    "request_num": index,
                    "status_code": None,
                    "error": str(e),
                    "was_blocked": False
                }
        
        # Execute requests
        if concurrent:
            # Send all at once (more aggressive)
            tasks = [send_request(i) for i in range(num_requests)]
            responses = await asyncio.gather(*tasks)
        else:
            # Send sequentially (more realistic)
            responses = []
            for i in range(num_requests):
                response = await send_request(i)
                responses.append(response)
                # Small delay between requests
                await asyncio.sleep(0.01)
        
        # Analyze results
        for resp in responses:
            results["responses"].append(resp)
            if resp.get("was_blocked"):
                results["blocked"] += 1
            else:
                results["successful"] += 1
        
        return results


class SimulationAnalyzer:
    """Analyze simulation results and provide insights."""
    
    ATTACK_EXPLANATIONS = {
        AttackType.INVALID_SIGNATURE: {
            "what_attempted": "Attacker sent a webhook with an invalid HMAC signature",
            "how_blocked": "HMAC-SHA256 signature verification failed at the authentication middleware",
            "why_matters": "Ensures webhook authenticity and prevents man-in-the-middle attacks",
            "attack_vector": "Network interception or spoofed webhook source",
            "mitigation": "WebShield verifies every webhook signature using a shared secret with the provider",
            "security_principle": "Authentication & Integrity Verification"
        },
        AttackType.TAMPERED_PAYLOAD: {
            "what_attempted": "Attacker modified the payload after signing",
            "how_blocked": "Payload hash verification detected modification",
            "why_matters": "Detects when webhook data has been tampered with in transit",
            "attack_vector": "Man-in-the-middle modification of webhook data",
            "mitigation": "WebShield computes SHA256 hash of payload and compares against transmitted hash",
            "security_principle": "Data Integrity & Tampering Detection"
        },
        AttackType.REPLAY_ATTACK: {
            "what_attempted": "Attacker re-sent the same webhook request twice",
            "how_blocked": "Redis-based request_id deduplication detected duplicate",
            "why_matters": "Prevents processing the same event multiple times (prevents duplicate transactions)",
            "attack_vector": "Capturing and replaying valid webhooks to cause duplicate effects",
            "mitigation": "WebShield stores request_id in Redis with 5-minute expiry to detect replays",
            "security_principle": "Idempotency & Replay Protection"
        },
        AttackType.RATE_LIMIT: {
            "what_attempted": "Attacker flooded the webhook endpoint with 150+ requests in 60 seconds",
            "how_blocked": "Token bucket rate limiter rejected requests after limit exceeded (100 req/60s)",
            "why_matters": "Protects against DDoS attacks that could overwhelm internal services",
            "attack_vector": "Volume-based DDoS attack to cause service degradation",
            "mitigation": "WebShield uses atomic Redis Lua scripts to enforce per-provider rate limits",
            "security_principle": "DDoS Protection & Resource Management"
        },
        AttackType.OLD_TIMESTAMP: {
            "what_attempted": "Attacker sent a webhook with a timestamp > 5 minutes old",
            "how_blocked": "Timestamp validation rejected request outside acceptable time window",
            "why_matters": "Prevents processing of old requests that might be replays or delayed attacks",
            "attack_vector": "Delayed replay of captured webhooks from hours/days ago",
            "mitigation": "WebShield validates timestamp is within 5-minute window of current time",
            "security_principle": "Temporal Validation & Freshness"
        },
        AttackType.FUTURE_TIMESTAMP: {
            "what_attempted": "Attacker sent a webhook with a future timestamp (clock skew attack)",
            "how_blocked": "Timestamp validation rejected request with invalid future timestamp",
            "why_matters": "Prevents spoofed webhooks with manipulated timestamps",
            "attack_vector": "Forged webhooks pretending to be from the future",
            "mitigation": "WebShield rejects any timestamp more than 5 minutes in the future",
            "security_principle": "Clock Integrity & Temporal Validation"
        },
        AttackType.MISSING_SIGNATURE: {
            "what_attempted": "Attacker sent a webhook without the required signature header",
            "how_blocked": "Authentication middleware rejected unauthenticated request",
            "why_matters": "Ensures all webhooks are authenticated",
            "attack_vector": "Forged webhooks from unknown sources",
            "mitigation": "WebShield requires X-Webhook-Signature header on all incoming webhooks",
            "security_principle": "Authentication Requirement"
        },
        AttackType.MALFORMED_JSON: {
            "what_attempted": "Attacker sent invalid JSON that can't be parsed",
            "how_blocked": "JSON parsing validation rejected malformed request",
            "why_matters": "Prevents application crashes from invalid data",
            "attack_vector": "Sending corrupted data to crash webhook processors",
            "mitigation": "WebShield validates JSON structure before forwarding",
            "security_principle": "Input Validation & Sanitization"
        },
        AttackType.OVERSIZED_PAYLOAD: {
            "what_attempted": "Attacker sent a payload larger than maximum allowed size",
            "how_blocked": "Payload size validation rejected oversized request",
            "why_matters": "Prevents memory exhaustion and DoS attacks",
            "attack_vector": "Memory exhaustion by flooding with huge payloads",
            "mitigation": "WebShield enforces configurable max payload size limit",
            "security_principle": "Denial of Service Prevention & Resource Protection"
        }
    }
    
    @staticmethod
    def analyze_result(
        attack_type: AttackType,
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze attack result and provide educational insights.
        
        Returns:
            Dictionary with analysis and explanations
        """
        was_blocked = execution_result.get("was_blocked", False)
        status_code = execution_result.get("status_code")
        error_type = execution_result.get("error_type")
        success = execution_result.get("success", True)
        
        explanation = SimulationAnalyzer.ATTACK_EXPLANATIONS.get(
            attack_type,
            {
                "what_attempted": f"Attempted {attack_type} attack",
                "how_blocked": "Security check prevented the attack",
                "why_matters": "Protects your webhook infrastructure",
                "attack_vector": "Unknown",
                "mitigation": "WebShield protection in place"
            }
        )
        
        # Determine block reason from status code and error type
        block_reason = "Unknown"
        
        if error_type == "timeout":
            block_reason = "Request timeout - webhook endpoint not responding"
        elif error_type == "connection_error":
            block_reason = "Connection failed - webhook endpoint unreachable"
        elif error_type == "execution_error":
            block_reason = "Execution error - failed to send attack"
        elif status_code == 401:
            block_reason = "Authentication failed - invalid or missing signature"
        elif status_code == 403:
            block_reason = "Forbidden - security policy violation"
        elif status_code == 409:
            block_reason = "Conflict - replay attack detected"
        elif status_code == 429:
            block_reason = "Too Many Requests - rate limit exceeded"
        elif status_code == 400:
            block_reason = "Bad Request - payload validation failed"
        elif status_code == 413:
            block_reason = "Payload Too Large"
        elif status_code == 404:
            block_reason = "Not Found - webhook endpoint not found"
        elif status_code and status_code >= 400:
            block_reason = f"HTTP {status_code} - Request blocked"
        elif status_code and status_code < 400:
            block_reason = f"HTTP {status_code} - Request allowed (unexpected)"
        
        return {
            "attack_type": attack_type,
            "was_blocked": was_blocked,
            "block_reason": block_reason,
            "status_code": status_code,
            "error_type": error_type,
            "success": success,
            "explanation": explanation,
            "recommendation": (
                "✅ Security working as expected!" if (was_blocked and success)
                else "⚠️ Unexpected result - check webhook configuration" if not success
                else "⚠️ Attack was not blocked - review security settings"
            )
        }
