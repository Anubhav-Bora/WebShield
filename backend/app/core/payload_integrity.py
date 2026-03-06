"""
Payload integrity checking utilities.

Detects if webhook payloads have been tampered with using SHA256 hashing.
"""
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


def calculate_payload_hash(payload: dict) -> str:
    """
    Calculate SHA256 hash of webhook payload.
    
    Args:
        payload: Webhook payload dictionary
    
    Returns:
        SHA256 hash as hex string
    """
    # Convert payload to JSON string with sorted keys for consistency
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    
    # Calculate SHA256 hash
    hash_obj = hashlib.sha256(payload_json.encode('utf-8'))
    return hash_obj.hexdigest()


def verify_payload_integrity(payload: dict, stored_hash: str) -> bool:
    """
    Verify if payload matches stored hash.
    
    Args:
        payload: Webhook payload dictionary
        stored_hash: Previously stored SHA256 hash
    
    Returns:
        True if payload matches hash, False if tampered
    """
    current_hash = calculate_payload_hash(payload)
    return current_hash == stored_hash


def detect_payload_changes(original_payload: dict, current_payload: dict) -> dict:
    """
    Detect what changed between two payloads.
    
    Args:
        original_payload: Original payload
        current_payload: Current payload
    
    Returns:
        Dictionary with changes detected
    """
    changes = {
        "added_fields": [],
        "removed_fields": [],
        "modified_fields": [],
        "is_tampered": False
    }
    
    original_keys = set(original_payload.keys())
    current_keys = set(current_payload.keys())
    
    # Check for added fields
    added = current_keys - original_keys
    if added:
        changes["added_fields"] = list(added)
        changes["is_tampered"] = True
    
    # Check for removed fields
    removed = original_keys - current_keys
    if removed:
        changes["removed_fields"] = list(removed)
        changes["is_tampered"] = True
    
    # Check for modified fields
    for key in original_keys & current_keys:
        if original_payload[key] != current_payload[key]:
            changes["modified_fields"].append({
                "field": key,
                "original": original_payload[key],
                "current": current_payload[key]
            })
            changes["is_tampered"] = True
    
    return changes
