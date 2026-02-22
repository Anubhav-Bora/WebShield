"""
Security utilities for webhook verification.

Includes HMAC signature verification and constant-time comparison.
"""
import hmac
import hashlib


def verify_hmac_signature(
    payload: bytes,
    secret_key: str,
    received_signature: str
) -> bool:
    """
    Verify HMAC SHA256 signature using constant-time comparison.
    
    Args:
        payload: The webhook payload (raw bytes)
        secret_key: The shared secret key from the provider
        received_signature: The signature from the webhook header
    
    Returns:
        True if signature is valid, False otherwise
    
    Why constant-time comparison?
    - Prevents timing attacks where attackers measure response time
    - hmac.compare_digest() always takes the same time regardless of match
    """
    # Calculate expected signature
    expected_signature = hmac.new(
        secret_key.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Use constant-time comparison (safe against timing attacks)
    return hmac.compare_digest(received_signature, expected_signature)
