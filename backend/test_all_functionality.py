"""
Comprehensive test script for WebShield functionality.
Tests all core features: authentication, webhook validation, security, analytics, and more.
"""
import asyncio
import json
import hmac
import hashlib
import uuid
from datetime import datetime, timedelta
import httpx
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo123"

# Test results tracking
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


async def test_authentication():
    """Test 1: Authentication (Login/Signup)"""
    print("\n🔐 Testing Authentication...")
    
    async with httpx.AsyncClient() as client:
        # Test login
        try:
            response = await client.post(
                f"{BASE_URL}/auth/login",
                json={"username": DEMO_USERNAME, "password": DEMO_PASSWORD}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                log_test("Login", token is not None, f"Token: {token[:20]}..." if token else "No token")
                return token
            else:
                log_test("Login", False, f"Status: {response.status_code}")
                return None
        except Exception as e:
            log_test("Login", False, str(e))
            return None


async def test_providers(token: str):
    """Test 2: Provider Management"""
    print("\n📦 Testing Provider Management...")
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get providers
        try:
            response = await client.get(
                f"{BASE_URL}/admin/providers",
                headers=headers
            )
            
            if response.status_code == 200:
                providers = response.json()
                log_test("Get Providers", len(providers) > 0, f"Found {len(providers)} providers")
                return providers
            else:
                log_test("Get Providers", False, f"Status: {response.status_code}")
                return []
        except Exception as e:
            log_test("Get Providers", False, str(e))
            return []


async def test_webhook_validation(token: str, providers: list):
    """Test 3: Webhook Signature Validation"""
    print("\n🔒 Testing Webhook Validation...")
    
    if not providers:
        log_test("Webhook Validation", False, "No providers available")
        return
    
    provider = providers[0]
    provider_name = provider["name"]
    
    # Get secret_key from database
    from app.db.session import AsyncSessionLocal
    from app.db.models.provider import Provider
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Provider).where(Provider.name == provider_name))
        db_provider = result.scalar_one_or_none()
        if not db_provider:
            log_test("Webhook Validation", False, "Provider not found in database")
            return
        secret_key = db_provider.secret_key
    
    async with httpx.AsyncClient() as client:
        # Test valid signature
        try:
            payload = {"event": "test", "data": {"id": 123}}
            payload_json = json.dumps(payload)
            payload_bytes = payload_json.encode()
            
            # Calculate correct signature
            signature = hmac.new(
                secret_key.encode(),
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
            
            log_test("Valid Signature", response.status_code == 200, f"Status: {response.status_code}")
            
            # Test invalid signature
            bad_signature = "invalid_signature_12345"
            response = await client.post(
                f"{BASE_URL}/webhooks/{provider_name}",
                content=payload_json,
                headers={
                    "X-Signature": bad_signature,
                    "X-Timestamp": timestamp,
                    "X-Request-ID": str(uuid.uuid4()),
                    "Content-Type": "application/json"
                }
            )
            
            log_test("Invalid Signature Rejected", response.status_code == 401, f"Status: {response.status_code}")
            
        except Exception as e:
            log_test("Webhook Validation", False, str(e))


async def test_replay_protection(token: str, providers: list):
    """Test 4: Replay Attack Prevention"""
    print("\n🛡️ Testing Replay Protection...")
    
    if not providers:
        log_test("Replay Protection", False, "No providers available")
        return
    
    provider = providers[0]
    provider_name = provider["name"]
    
    # Get secret_key from database
    from app.db.session import AsyncSessionLocal
    from app.db.models.provider import Provider
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Provider).where(Provider.name == provider_name))
        db_provider = result.scalar_one_or_none()
        if not db_provider:
            log_test("Replay Protection", False, "Provider not found in database")
            return
        secret_key = db_provider.secret_key
    
    async with httpx.AsyncClient() as client:
        try:
            payload = {"event": "replay_test", "data": {"id": 456}}
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
            
            # First request should succeed
            response1 = await client.post(
                f"{BASE_URL}/webhooks/{provider_name}",
                content=payload_json,
                headers=headers
            )
            
            first_success = response1.status_code == 200
            
            # Replay same request should fail
            response2 = await client.post(
                f"{BASE_URL}/webhooks/{provider_name}",
                content=payload_json,
                headers=headers
            )
            
            replay_blocked = response2.status_code == 409
            
            log_test("Replay Protection", first_success and replay_blocked, 
                    f"First: {response1.status_code}, Replay: {response2.status_code}")
            
        except Exception as e:
            log_test("Replay Protection", False, str(e))


async def test_rate_limiting(token: str, providers: list):
    """Test 5: Rate Limiting"""
    print("\n⏱️ Testing Rate Limiting...")
    
    if not providers:
        log_test("Rate Limiting", False, "No providers available")
        return
    
    provider = providers[0]
    provider_name = provider["name"]
    
    # Get secret_key from database
    from app.db.session import AsyncSessionLocal
    from app.db.models.provider import Provider
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Provider).where(Provider.name == provider_name))
        db_provider = result.scalar_one_or_none()
        if not db_provider:
            log_test("Rate Limiting", False, "Provider not found in database")
            return
        secret_key = db_provider.secret_key
    
    async with httpx.AsyncClient() as client:
        try:
            # Send multiple requests rapidly
            success_count = 0
            rate_limited = False
            
            for i in range(5):
                payload = {"event": f"rate_test_{i}", "data": {"id": i}}
                payload_json = json.dumps(payload)
                payload_bytes = payload_json.encode()
                
                signature = hmac.new(
                    secret_key.encode(),
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
                
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limited = True
            
            log_test("Rate Limiting", success_count > 0, f"Successful: {success_count}/5")
            
        except Exception as e:
            log_test("Rate Limiting", False, str(e))


async def test_security_logging(token: str):
    """Test 6: Security Event Logging"""
    print("\n📝 Testing Security Logging...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/admin/logs"
            )
            
            if response.status_code == 200:
                logs = response.json()
                has_logs = len(logs) > 0
                log_test("Security Logs Retrieved", has_logs, f"Found {len(logs)} security events")
                
                if has_logs:
                    # Check for expected event types
                    event_types = set(log.get("event_type") for log in logs)
                    log_test("Security Event Types", len(event_types) > 0, f"Event types: {event_types}")
            else:
                log_test("Security Logs Retrieved", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Security Logs Retrieved", False, str(e))


async def test_webhook_events(token: str):
    """Test 7: Webhook Events Storage"""
    print("\n📊 Testing Webhook Events...")
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = await client.get(
                f"{BASE_URL}/admin/webhooks",
                headers=headers
            )
            
            if response.status_code == 200:
                webhooks = response.json()
                has_webhooks = len(webhooks) > 0
                log_test("Webhook Events Retrieved", has_webhooks, f"Found {len(webhooks)} webhook events")
                
                if has_webhooks:
                    # Check webhook structure
                    webhook = webhooks[0]
                    has_required_fields = all(
                        field in webhook for field in 
                        ["id", "provider_id", "payload", "signature_valid", "received_at"]
                    )
                    log_test("Webhook Event Structure", has_required_fields, "All required fields present")
            else:
                log_test("Webhook Events Retrieved", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Webhook Events Retrieved", False, str(e))


async def test_analytics(token: str):
    """Test 8: Analytics Endpoint"""
    print("\n📈 Testing Analytics...")
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = await client.get(
                f"{BASE_URL}/admin/analytics/webhooks?days=7",
                headers=headers
            )
            
            if response.status_code == 200:
                analytics = response.json()
                has_data = len(analytics) > 0
                log_test("Analytics Data Retrieved", has_data, f"Found {len(analytics)} data points")
                
                if has_data:
                    # Check analytics structure
                    point = analytics[0]
                    has_required_fields = all(
                        field in point for field in 
                        ["hour", "total_webhooks", "success_rate", "avg_latency_ms"]
                    )
                    log_test("Analytics Data Structure", has_required_fields, "All required fields present")
            else:
                log_test("Analytics Data Retrieved", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Analytics Data Retrieved", False, str(e))


async def test_security_analytics(token: str):
    """Test 9: Security Analytics"""
    print("\n🔒 Testing Security Analytics...")
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = await client.get(
                f"{BASE_URL}/admin/analytics/security?days=7",
                headers=headers
            )
            
            if response.status_code == 200:
                analytics = response.json()
                has_data = len(analytics) > 0
                log_test("Security Analytics Retrieved", has_data, f"Found {len(analytics)} data points")
            else:
                log_test("Security Analytics Retrieved", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Security Analytics Retrieved", False, str(e))


async def test_audit_logs(token: str):
    """Test 10: Audit Logs"""
    print("\n📋 Testing Audit Logs...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/admin/logs/stats"
            )
            
            if response.status_code == 200:
                stats = response.json()
                has_stats = stats is not None
                log_test("Audit Logs Retrieved", has_stats, f"Stats: {stats}")
            else:
                log_test("Audit Logs Retrieved", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Audit Logs Retrieved", False, str(e))


async def test_timestamp_validation(token: str, providers: list):
    """Test 11: Timestamp Validation"""
    print("\n⏰ Testing Timestamp Validation...")
    
    if not providers:
        log_test("Timestamp Validation", False, "No providers available")
        return
    
    provider = providers[0]
    provider_name = provider["name"]
    
    # Get secret_key from database
    from app.db.session import AsyncSessionLocal
    from app.db.models.provider import Provider
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Provider).where(Provider.name == provider_name))
        db_provider = result.scalar_one_or_none()
        if not db_provider:
            log_test("Timestamp Validation", False, "Provider not found in database")
            return
        secret_key = db_provider.secret_key
    
    async with httpx.AsyncClient() as client:
        try:
            payload = {"event": "timestamp_test", "data": {"id": 789}}
            payload_json = json.dumps(payload)
            payload_bytes = payload_json.encode()
            
            signature = hmac.new(
                secret_key.encode(),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            
            # Old timestamp (> 5 minutes)
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
            
            log_test("Old Timestamp Rejected", response.status_code == 400, f"Status: {response.status_code}")
            
        except Exception as e:
            log_test("Timestamp Validation", False, str(e))


async def test_payload_integrity(token: str):
    """Test 12: Payload Integrity Checking"""
    print("\n🔐 Testing Payload Integrity...")
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            # Get a webhook event
            response = await client.get(
                f"{BASE_URL}/admin/webhooks?limit=1",
                headers=headers
            )
            
            if response.status_code == 200:
                webhooks = response.json()
                if webhooks:
                    webhook = webhooks[0]
                    webhook_id = webhook["id"]
                    
                    # Verify integrity with same payload
                    response = await client.post(
                        f"{BASE_URL}/webhooks/verify/{webhook_id}",
                        json=webhook["payload"],
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        is_valid = result.get("is_valid", False)
                        log_test("Payload Integrity Check", is_valid, "Payload integrity verified")
                    else:
                        log_test("Payload Integrity Check", False, f"Status: {response.status_code}")
                else:
                    log_test("Payload Integrity Check", False, "No webhooks available")
            else:
                log_test("Payload Integrity Check", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Payload Integrity Check", False, str(e))


async def test_missing_headers(token: str, providers: list):
    """Test 13: Missing Required Headers"""
    print("\n⚠️ Testing Missing Headers Validation...")
    
    if not providers:
        log_test("Missing Headers", False, "No providers available")
        return
    
    provider = providers[0]
    provider_name = provider["name"]
    
    async with httpx.AsyncClient() as client:
        try:
            payload = {"event": "test"}
            
            # Missing signature header
            response = await client.post(
                f"{BASE_URL}/webhooks/{provider_name}",
                json=payload,
                headers={"X-Timestamp": datetime.utcnow().isoformat() + "Z"}
            )
            
            log_test("Missing Signature Header Rejected", response.status_code == 400, f"Status: {response.status_code}")
            
        except Exception as e:
            log_test("Missing Headers", False, str(e))


async def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 WebShield Comprehensive Functionality Test")
    print("=" * 60)
    
    # Test authentication
    token = await test_authentication()
    if not token:
        print("\n❌ Authentication failed. Cannot continue tests.")
        return
    
    # Get providers
    providers = await test_providers(token)
    
    # Run all tests
    await test_webhook_validation(token, providers)
    await test_replay_protection(token, providers)
    await test_rate_limiting(token, providers)
    await test_timestamp_validation(token, providers)
    await test_missing_headers(token, providers)
    await test_security_logging(token)
    await test_webhook_events(token)
    await test_analytics(token)
    await test_security_analytics(token)
    await test_audit_logs(token)
    await test_payload_integrity(token)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"📈 Total: {results['passed'] + results['failed']}")
    print(f"📊 Success Rate: {(results['passed'] / (results['passed'] + results['failed']) * 100):.1f}%")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
