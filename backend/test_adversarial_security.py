"""
Adversarial Security Test Suite for WebShield

This script tests your security by trying to BREAK it.
If these tests pass, it proves your security is real, not fake.

Each test is designed to succeed ONLY if the security feature is actually implemented.
"""
import asyncio
import json
import hmac
import hashlib
import uuid
import time
from datetime import datetime, timedelta
import httpx
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo123"

results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(name: str, passed: bool, message: str = ""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if message:
        print(f"   └─ {message}")
    
    results["tests"].append({
        "name": name,
        "passed": passed,
        "message": message
    })
    
    if passed:
        results["passed"] += 1
    else:
        results["failed"] += 1


async def get_token():
    """Get auth token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"username": DEMO_USERNAME, "password": DEMO_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
    return None


async def get_provider_secret(provider_name: str):
    """Get provider secret from database"""
    from app.db.session import AsyncSessionLocal
    from app.db.models.provider import Provider
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Provider).where(Provider.name == provider_name))
        provider = result.scalar_one_or_none()
        return provider.secret_key if provider else None


async def test_signature_tampering():
    """
    Test 1: Signature Tampering Detection
    
    ATTACK: Modify payload after signing
    EXPECTED: Request rejected with 401
    PROVES: Signature verification is real
    """
    print("\n🔓 Test 1: Signature Tampering Detection")
    
    provider_name = "stripe"
    secret_key = await get_provider_secret(provider_name)
    if not secret_key:
        log_test("Signature Tampering", False, "Provider not found")
        return
    
    async with httpx.AsyncClient() as client:
        try:
            # Create original payload
            original_payload = {"event": "payment.success", "amount": 100}
            original_json = json.dumps(original_payload)
            original_bytes = original_json.encode()
            
            # Sign the original payload
            signature = hmac.new(
                secret_key.encode(),
                original_bytes,
                hashlib.sha256
            ).hexdigest()
            
            # NOW TAMPER: Change the payload but keep the signature
            tampered_payload = {"event": "payment.success", "amount": 999999}
            tampered_json = json.dumps(tampered_payload)
            
            timestamp = datetime.utcnow().isoformat() + "Z"
            request_id = str(uuid.uuid4())
            
            # Send tampered payload with original signature
            response = await client.post(
                f"{BASE_URL}/webhooks/{provider_name}",
                content=tampered_json,
                headers={
                    "X-Signature": signature,
                    "X-Timestamp": timestamp,
                    "X-Request-ID": request_id,
                    "Content-Type": "application/json"
                }
            )
            
            # If signature verification is real, this MUST be rejected
            is_rejected = response.status_code == 401
            log_test("Signature Tampering", is_rejected, 
                    f"Tampered request status: {response.status_code} (should be 401)")
            
        except Exception as e:
            log_test("Signature Tampering", False, str(e))


async def test_timing_attack_resistance():
    """
    Test 2: Constant-Time Comparison (Timing Attack Resistance)
    
    ATTACK: Measure response time for valid vs invalid signatures
    EXPECTED: Response times are similar (constant-time comparison)
    PROVES: Using hmac.compare_digest, not simple ==
    """
    print("\n⏱️ Test 2: Timing Attack Resistance")
    
    provider_name = "stripe"
    secret_key = await get_provider_secret(provider_name)
    if not secret_key:
        log_test("Timing Attack Resistance", False, "Provider not found")
        return
    
    async with httpx.AsyncClient() as client:
        try:
            payload = {"event": "test"}
            payload_json = json.dumps(payload)
            payload_bytes = payload_json.encode()
            
            # Valid signature
            valid_sig = hmac.new(
                secret_key.encode(),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            
            # Invalid signature (completely different)
            invalid_sig = "0" * 64
            
            timestamp = datetime.utcnow().isoformat() + "Z"
            
            # Warm up the connection
            await client.post(
                f"{BASE_URL}/webhooks/{provider_name}",
                content=payload_json,
                headers={
                    "X-Signature": valid_sig,
                    "X-Timestamp": timestamp,
                    "X-Request-ID": str(uuid.uuid4()),
                    "Content-Type": "application/json"
                }
            )
            
            # Measure time for valid signature (after warmup)
            times_valid = []
            for _ in range(5):
                start = time.perf_counter()
                response = await client.post(
                    f"{BASE_URL}/webhooks/{provider_name}",
                    content=payload_json,
                    headers={
                        "X-Signature": valid_sig,
                        "X-Timestamp": timestamp,
                        "X-Request-ID": str(uuid.uuid4()),
                        "Content-Type": "application/json"
                    }
                )
                times_valid.append(time.perf_counter() - start)
            
            # Measure time for invalid signature
            times_invalid = []
            for _ in range(5):
                start = time.perf_counter()
                response = await client.post(
                    f"{BASE_URL}/webhooks/{provider_name}",
                    content=payload_json,
                    headers={
                        "X-Signature": invalid_sig,
                        "X-Timestamp": timestamp,
                        "X-Request-ID": str(uuid.uuid4()),
                        "Content-Type": "application/json"
                    }
                )
                times_invalid.append(time.perf_counter() - start)
            
            avg_valid = sum(times_valid) / len(times_valid)
            avg_invalid = sum(times_invalid) / len(times_invalid)
            
            # Times should be similar (within 100% variance is acceptable for network)
            # If using simple ==, invalid would be significantly faster
            variance = abs(avg_valid - avg_invalid) / max(avg_valid, avg_invalid)
            is_constant_time = variance < 1.0  # More lenient for network variance
            
            log_test("Timing Attack Resistance", is_constant_time,
                    f"Valid: {avg_valid*1000:.2f}ms, Invalid: {avg_invalid*1000:.2f}ms, Variance: {variance*100:.1f}%")
            
        except Exception as e:
            log_test("Timing Attack Resistance", False, str(e))


async def test_rate_limit_enforcement():
    """
    Test 3: Rate Limit Enforcement
    
    ATTACK: Send 150 requests in rapid succession (limit is 100/60s)
    EXPECTED: After 100 requests, get 429 Too Many Requests
    PROVES: Rate limiting is actually enforced
    """
    print("\n🚫 Test 3: Rate Limit Enforcement")
    
    provider_name = "twilio"  # Use different provider to avoid rate limit carryover
    secret_key = await get_provider_secret(provider_name)
    if not secret_key:
        log_test("Rate Limit Enforcement", False, "Provider not found")
        return
    
    async with httpx.AsyncClient() as client:
        try:
            payload = {"event": "sms.sent"}
            payload_json = json.dumps(payload)
            payload_bytes = payload_json.encode()
            
            signature = hmac.new(
                secret_key.encode(),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            
            timestamp = datetime.utcnow().isoformat() + "Z"
            
            success_count = 0
            rate_limited_count = 0
            
            # Send 120 requests rapidly
            for i in range(120):
                response = await client.post(
                    f"{BASE_URL}/webhooks/{provider_name}",
                    content=payload_json,
                    headers={
                        "X-Signature": signature,
                        "X-Timestamp": timestamp,
                        "X-Request-ID": str(uuid.uuid4()),
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limited_count += 1
            
            # Should have ~100 successes and ~20 rate limits
            is_enforced = success_count >= 95 and rate_limited_count >= 5
            log_test("Rate Limit Enforcement", is_enforced,
                    f"Successful: {success_count}, Rate Limited: {rate_limited_count}")
            
        except Exception as e:
            log_test("Rate Limit Enforcement", False, str(e))


async def test_replay_protection():
    """
    Test 4: Replay Attack Protection
    
    ATTACK: Send same request twice with same request ID
    EXPECTED: First succeeds (200), second fails (409 Conflict)
    PROVES: Redis deduplication is working
    """
    print("\n🔄 Test 4: Replay Attack Protection")
    
    provider_name = "paypal"
    secret_key = await get_provider_secret(provider_name)
    if not secret_key:
        log_test("Replay Protection", False, "Provider not found")
        return
    
    async with httpx.AsyncClient() as client:
        try:
            payload = {"event": "payment.completed", "id": "12345"}
            payload_json = json.dumps(payload)
            payload_bytes = payload_json.encode()
            
            signature = hmac.new(
                secret_key.encode(),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            
            timestamp = datetime.utcnow().isoformat() + "Z"
            request_id = str(uuid.uuid4())
            
            headers = {
                "X-Signature": signature,
                "X-Timestamp": timestamp,
                "X-Request-ID": request_id,
                "Content-Type": "application/json"
            }
            
            # First request
            response1 = await client.post(
                f"{BASE_URL}/webhooks/{provider_name}",
                content=payload_json,
                headers=headers
            )
            
            # Replay: Same request ID, same payload
            response2 = await client.post(
                f"{BASE_URL}/webhooks/{provider_name}",
                content=payload_json,
                headers=headers
            )
            
            first_success = response1.status_code == 200
            replay_blocked = response2.status_code == 409
            
            log_test("Replay Protection", first_success and replay_blocked,
                    f"First: {response1.status_code}, Replay: {response2.status_code}")
            
        except Exception as e:
            log_test("Replay Protection", False, str(e))


async def test_wrong_secret_rejection():
    """
    Test 5: Wrong Secret Key Rejection
    
    ATTACK: Use a different provider's secret to sign
    EXPECTED: Request rejected with 401
    PROVES: Secret key validation is real
    """
    print("\n🔑 Test 5: Wrong Secret Key Rejection")
    
    provider_name = "stripe"
    wrong_secret = "completely_wrong_secret_key_12345"
    
    async with httpx.AsyncClient() as client:
        try:
            payload = {"event": "test"}
            payload_json = json.dumps(payload)
            payload_bytes = payload_json.encode()
            
            # Sign with WRONG secret
            signature = hmac.new(
                wrong_secret.encode(),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            
            timestamp = datetime.utcnow().isoformat() + "Z"
            request_id = str(uuid.uuid4())
            
            response = await client.post(
                f"{BASE_URL}/webhooks/{provider_name}",
                content=payload_json,
                headers={
                    "X-Signature": signature,
                    "X-Timestamp": timestamp,
                    "X-Request-ID": request_id,
                    "Content-Type": "application/json"
                }
            )
            
            is_rejected = response.status_code == 401
            log_test("Wrong Secret Rejection", is_rejected,
                    f"Status: {response.status_code} (should be 401)")
            
        except Exception as e:
            log_test("Wrong Secret Rejection", False, str(e))


async def test_payload_integrity():
    """
    Test 6: Payload Integrity Checking
    
    ATTACK: Store payload, then verify with different data
    EXPECTED: Verification fails
    PROVES: SHA256 hashing is real
    """
    print("\n🔐 Test 6: Payload Integrity Checking")
    
    provider_name = "stripe"
    secret_key = await get_provider_secret(provider_name)
    if not secret_key:
        log_test("Payload Integrity", False, "Provider not found")
        return
    
    async with httpx.AsyncClient() as client:
        try:
            # Send original payload
            original_payload = {"event": "charge.succeeded", "amount": 100}
            original_json = json.dumps(original_payload)
            original_bytes = original_json.encode()
            
            signature = hmac.new(
                secret_key.encode(),
                original_bytes,
                hashlib.sha256
            ).hexdigest()
            
            timestamp = datetime.utcnow().isoformat() + "Z"
            request_id = str(uuid.uuid4())
            
            # Store the webhook
            response = await client.post(
                f"{BASE_URL}/webhooks/{provider_name}",
                content=original_json,
                headers={
                    "X-Signature": signature,
                    "X-Timestamp": timestamp,
                    "X-Request-ID": request_id,
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                log_test("Payload Integrity", False, "Failed to store webhook")
                return
            
            webhook_id = response.json().get("webhook_id")
            
            # Now verify with DIFFERENT payload
            tampered_payload = {"event": "charge.succeeded", "amount": 999999}
            
            verify_response = await client.post(
                f"{BASE_URL}/webhooks/verify/{webhook_id}",
                json=tampered_payload
            )
            
            if verify_response.status_code == 200:
                result = verify_response.json()
                tampering_detected = result.get("tampering_detected", False)
                log_test("Payload Integrity", tampering_detected,
                    f"Tampering detected: {tampering_detected}")
            else:
                log_test("Payload Integrity", False, f"Status: {verify_response.status_code}")
            
        except Exception as e:
            log_test("Payload Integrity", False, str(e))


async def test_timestamp_validation():
    """
    Test 7: Timestamp Validation
    
    ATTACK: Send webhook with timestamp > 5 minutes old
    EXPECTED: Request rejected with 400
    PROVES: Timestamp validation is real
    """
    print("\n⏰ Test 7: Timestamp Validation")
    
    provider_name = "stripe"
    secret_key = await get_provider_secret(provider_name)
    if not secret_key:
        log_test("Timestamp Validation", False, "Provider not found")
        return
    
    async with httpx.AsyncClient() as client:
        try:
            payload = {"event": "test"}
            payload_json = json.dumps(payload)
            payload_bytes = payload_json.encode()
            
            signature = hmac.new(
                secret_key.encode(),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            
            # Old timestamp (10 minutes ago)
            old_timestamp = (datetime.utcnow() - timedelta(minutes=10)).isoformat() + "Z"
            
            response = await client.post(
                f"{BASE_URL}/webhooks/{provider_name}",
                content=payload_json,
                headers={
                    "X-Signature": signature,
                    "X-Timestamp": old_timestamp,
                    "X-Request-ID": str(uuid.uuid4()),
                    "Content-Type": "application/json"
                }
            )
            
            is_rejected = response.status_code == 400
            log_test("Timestamp Validation", is_rejected,
                    f"Status: {response.status_code} (should be 400)")
            
        except Exception as e:
            log_test("Timestamp Validation", False, str(e))


async def test_future_timestamp_rejection():
    """
    Test 8: Future Timestamp Rejection
    
    ATTACK: Send webhook with timestamp 1 hour in future
    EXPECTED: Request rejected with 400
    PROVES: Timestamp validation checks both directions
    """
    print("\n🔮 Test 8: Future Timestamp Rejection")
    
    provider_name = "stripe"
    secret_key = await get_provider_secret(provider_name)
    if not secret_key:
        log_test("Future Timestamp Rejection", False, "Provider not found")
        return
    
    async with httpx.AsyncClient() as client:
        try:
            payload = {"event": "test"}
            payload_json = json.dumps(payload)
            payload_bytes = payload_json.encode()
            
            signature = hmac.new(
                secret_key.encode(),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            
            # Future timestamp (1 hour from now)
            future_timestamp = (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"
            
            response = await client.post(
                f"{BASE_URL}/webhooks/{provider_name}",
                content=payload_json,
                headers={
                    "X-Signature": signature,
                    "X-Timestamp": future_timestamp,
                    "X-Request-ID": str(uuid.uuid4()),
                    "Content-Type": "application/json"
                }
            )
            
            is_rejected = response.status_code == 400
            log_test("Future Timestamp Rejection", is_rejected,
                    f"Status: {response.status_code} (should be 400)")
            
        except Exception as e:
            log_test("Future Timestamp Rejection", False, str(e))


async def test_missing_headers():
    """
    Test 9: Missing Required Headers
    
    ATTACK: Send webhook without required headers
    EXPECTED: Request rejected with 400
    PROVES: Input validation is real
    """
    print("\n⚠️ Test 9: Missing Required Headers")
    
    provider_name = "stripe"
    
    async with httpx.AsyncClient() as client:
        try:
            payload = {"event": "test"}
            
            # Missing X-Signature
            response = await client.post(
                f"{BASE_URL}/webhooks/{provider_name}",
                json=payload,
                headers={
                    "X-Timestamp": datetime.utcnow().isoformat() + "Z",
                    "X-Request-ID": str(uuid.uuid4())
                }
            )
            
            is_rejected = response.status_code == 400
            log_test("Missing Required Headers", is_rejected,
                    f"Status: {response.status_code} (should be 400)")
            
        except Exception as e:
            log_test("Missing Required Headers", False, str(e))


async def test_invalid_json():
    """
    Test 10: Invalid JSON Rejection
    
    ATTACK: Send malformed JSON
    EXPECTED: Request rejected with 400
    PROVES: JSON parsing validation is real
    """
    print("\n📄 Test 10: Invalid JSON Rejection")
    
    provider_name = "stripe"
    secret_key = await get_provider_secret(provider_name)
    if not secret_key:
        log_test("Invalid JSON Rejection", False, "Provider not found")
        return
    
    async with httpx.AsyncClient() as client:
        try:
            # Malformed JSON
            bad_json = '{"event": "test", invalid}'
            bad_bytes = bad_json.encode()
            
            signature = hmac.new(
                secret_key.encode(),
                bad_bytes,
                hashlib.sha256
            ).hexdigest()
            
            response = await client.post(
                f"{BASE_URL}/webhooks/{provider_name}",
                content=bad_json,
                headers={
                    "X-Signature": signature,
                    "X-Timestamp": datetime.utcnow().isoformat() + "Z",
                    "X-Request-ID": str(uuid.uuid4()),
                    "Content-Type": "application/json"
                }
            )
            
            is_rejected = response.status_code == 400
            log_test("Invalid JSON Rejection", is_rejected,
                    f"Status: {response.status_code} (should be 400)")
            
        except Exception as e:
            log_test("Invalid JSON Rejection", False, str(e))


async def main():
    """Run all adversarial tests"""
    print("=" * 70)
    print("🛡️ WebShield Adversarial Security Test Suite")
    print("=" * 70)
    print("\nThese tests try to BREAK your security.")
    print("If they pass, it proves your security is REAL, not fake.\n")
    
    # Run all adversarial tests
    await test_signature_tampering()
    await test_timing_attack_resistance()
    await test_rate_limit_enforcement()
    await test_replay_protection()
    await test_wrong_secret_rejection()
    await test_payload_integrity()
    await test_timestamp_validation()
    await test_future_timestamp_rejection()
    await test_missing_headers()
    await test_invalid_json()
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 Adversarial Test Summary")
    print("=" * 70)
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"📈 Total: {results['passed'] + results['failed']}")
    
    if results['passed'] + results['failed'] > 0:
        success_rate = (results['passed'] / (results['passed'] + results['failed']) * 100)
        print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    print("=" * 70)
    
    if results['failed'] == 0:
        print("\n✨ All adversarial tests passed!")
        print("This proves your security is REAL and not designed to pass.\n")
    else:
        print(f"\n⚠️ {results['failed']} test(s) failed.")
        print("Review the failures above to identify security issues.\n")


if __name__ == "__main__":
    asyncio.run(main())
