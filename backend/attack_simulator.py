#!/usr/bin/env python3
"""
Attack Simulator Script - Demonstrates WebShield Security Features

This script:
1. Creates a test user and provider
2. Executes various attack scenarios
3. Shows real-time security logs on the dashboard

Run with: python attack_simulator.py
"""

import asyncio
import httpx
import json
import hmac
import hashlib
import uuid
from datetime import datetime, timedelta
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "attacker@test.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_PROVIDER_NAME = "attack-test-provider"
TEST_SECRET_KEY = "super_secret_key_12345"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_attack(attack_name, description):
    print(f"{Colors.CYAN}{Colors.BOLD}🔥 ATTACK: {attack_name}{Colors.ENDC}")
    print(f"{Colors.CYAN}   {description}{Colors.ENDC}\n")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.ENDC}")

def calculate_signature(payload: dict, secret: str) -> str:
    """Calculate HMAC-SHA256 signature"""
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    signature = hmac.new(
        secret.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

async def create_user(client: httpx.AsyncClient) -> str:
    """Create a test user and return auth token"""
    print_info(f"Creating user: {TEST_USER_EMAIL}")
    
    response = await client.post(
        f"{BASE_URL}/signup",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "username": "attacker_test"
        }
    )
    
    if response.status_code != 200:
        print_error(f"Failed to create user: {response.text}")
        return None
    
    # Login to get token
    response = await client.post(
        f"{BASE_URL}/login",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
    )
    
    if response.status_code != 200:
        print_error(f"Failed to login: {response.text}")
        return None
    
    token = response.json().get("access_token")
    print_success(f"User created and logged in. Token: {token[:20]}...")
    return token

async def create_provider(client: httpx.AsyncClient, token: str) -> dict:
    """Create a test provider"""
    print_info(f"Creating provider: {TEST_PROVIDER_NAME}")
    
    response = await client.post(
        f"{BASE_URL}/admin/providers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": TEST_PROVIDER_NAME,
            "secret_key": TEST_SECRET_KEY,
            "forwarding_url": "http://localhost:9000/webhook",
            "is_active": True
        }
    )
    
    if response.status_code != 200:
        print_error(f"Failed to create provider: {response.text}")
        return None
    
    provider = response.json()
    print_success(f"Provider created: {provider['id']}")
    return provider

async def send_webhook(payload: dict, signature: str = None, timestamp: str = None, request_id: str = None, tampered: bool = False) -> dict:
    """Send a webhook request"""
    headers = {
        "Content-Type": "application/json",
    }
    
    if signature:
        headers["X-Signature"] = signature
    if timestamp:
        headers["X-Timestamp"] = timestamp
    if request_id:
        headers["X-Request-ID"] = request_id
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/webhooks/{TEST_PROVIDER_NAME}",
                json=payload,
                headers=headers,
                timeout=5.0
            )
            return {
                "status_code": response.status_code,
                "body": response.json() if response.text else {},
                "success": response.status_code == 200
            }
        except Exception as e:
            return {
                "status_code": 0,
                "body": {"error": str(e)},
                "success": False
            }

async def attack_1_invalid_signature():
    """Attack 1: Invalid Signature"""
    print_attack(
        "Invalid Signature",
        "Sending webhook with tampered signature to bypass HMAC verification"
    )
    
    payload = {
        "event": "payment.completed",
        "amount": 1000,
        "customer_id": "cust_123"
    }
    
    # Calculate correct signature
    correct_sig = calculate_signature(payload, TEST_SECRET_KEY)
    
    # Tamper with signature
    tampered_sig = "0" * 64  # Invalid signature
    
    timestamp = datetime.utcnow().isoformat() + "Z"
    request_id = str(uuid.uuid4())
    
    print_info(f"Correct signature: {correct_sig[:16]}...")
    print_info(f"Tampered signature: {tampered_sig[:16]}...")
    
    result = await send_webhook(payload, tampered_sig, timestamp, request_id)
    
    if result["success"]:
        print_error("ATTACK SUCCEEDED - Signature validation failed!")
    else:
        print_success("ATTACK BLOCKED - Invalid signature rejected")
    
    print_info(f"Response: {result['body']}\n")
    await asyncio.sleep(1)

async def attack_2_replay_attack():
    """Attack 2: Replay Attack"""
    print_attack(
        "Replay Attack",
        "Resending the same webhook multiple times to bypass replay protection"
    )
    
    payload = {
        "event": "order.created",
        "order_id": "ord_456",
        "amount": 500
    }
    
    signature = calculate_signature(payload, TEST_SECRET_KEY)
    timestamp = datetime.utcnow().isoformat() + "Z"
    request_id = str(uuid.uuid4())
    
    print_info(f"Sending webhook with request_id: {request_id}")
    
    # First request should succeed
    result1 = await send_webhook(payload, signature, timestamp, request_id)
    print_info(f"First attempt: {result1['body']}")
    
    await asyncio.sleep(0.5)
    
    # Replay the same request
    print_info("Replaying the same request...")
    result2 = await send_webhook(payload, signature, timestamp, request_id)
    
    if result2["success"]:
        print_error("ATTACK SUCCEEDED - Replay protection failed!")
    else:
        print_success("ATTACK BLOCKED - Replay attempt detected and rejected")
    
    print_info(f"Response: {result2['body']}\n")
    await asyncio.sleep(1)

async def attack_3_rate_limiting():
    """Attack 3: Rate Limiting Bypass"""
    print_attack(
        "Rate Limiting Bypass",
        "Sending multiple webhooks rapidly to exceed rate limits"
    )
    
    print_info("Sending 15 webhooks in rapid succession (limit is 10/minute)...\n")
    
    blocked_count = 0
    success_count = 0
    
    for i in range(15):
        payload = {
            "event": f"test.event.{i}",
            "sequence": i
        }
        
        signature = calculate_signature(payload, TEST_SECRET_KEY)
        timestamp = datetime.utcnow().isoformat() + "Z"
        request_id = str(uuid.uuid4())
        
        result = await send_webhook(payload, signature, timestamp, request_id)
        
        if result["success"]:
            success_count += 1
            print_info(f"  Request {i+1}: ✓ Accepted")
        else:
            blocked_count += 1
            print_error(f"  Request {i+1}: ✗ Blocked - {result['body'].get('detail', 'Rate limited')}")
        
        await asyncio.sleep(0.1)
    
    print()
    if blocked_count > 0:
        print_success(f"ATTACK BLOCKED - Rate limiting enforced ({blocked_count} requests blocked)")
    else:
        print_error(f"ATTACK SUCCEEDED - No rate limiting detected ({success_count} requests accepted)")
    
    print_info(f"Accepted: {success_count}, Blocked: {blocked_count}\n")
    await asyncio.sleep(1)

async def attack_4_timestamp_tampering():
    """Attack 4: Timestamp Tampering"""
    print_attack(
        "Timestamp Tampering",
        "Sending webhook with old timestamp to bypass timestamp validation"
    )
    
    payload = {
        "event": "user.created",
        "user_id": "usr_789"
    }
    
    signature = calculate_signature(payload, TEST_SECRET_KEY)
    
    # Use timestamp from 10 minutes ago
    old_timestamp = (datetime.utcnow() - timedelta(minutes=10)).isoformat() + "Z"
    request_id = str(uuid.uuid4())
    
    print_info(f"Current time: {datetime.utcnow().isoformat()}Z")
    print_info(f"Webhook timestamp: {old_timestamp} (10 minutes old)")
    
    result = await send_webhook(payload, signature, old_timestamp, request_id)
    
    if result["success"]:
        print_error("ATTACK SUCCEEDED - Old timestamp accepted!")
    else:
        print_success("ATTACK BLOCKED - Old timestamp rejected")
    
    print_info(f"Response: {result['body']}\n")
    await asyncio.sleep(1)

async def attack_5_payload_tampering():
    """Attack 5: Payload Tampering"""
    print_attack(
        "Payload Tampering",
        "Modifying payload after signature calculation to bypass integrity check"
    )
    
    original_payload = {
        "event": "payment.completed",
        "amount": 100,
        "customer_id": "cust_999"
    }
    
    # Calculate signature with original payload
    signature = calculate_signature(original_payload, TEST_SECRET_KEY)
    
    # Tamper with payload
    tampered_payload = {
        "event": "payment.completed",
        "amount": 10000,  # Changed amount!
        "customer_id": "cust_999"
    }
    
    timestamp = datetime.utcnow().isoformat() + "Z"
    request_id = str(uuid.uuid4())
    
    print_info(f"Original payload: {json.dumps(original_payload)}")
    print_info(f"Tampered payload: {json.dumps(tampered_payload)}")
    print_info(f"Signature calculated for original payload")
    
    result = await send_webhook(tampered_payload, signature, timestamp, request_id)
    
    if result["success"]:
        print_error("ATTACK SUCCEEDED - Payload tampering not detected!")
    else:
        print_success("ATTACK BLOCKED - Payload tampering detected")
    
    print_info(f"Response: {result['body']}\n")
    await asyncio.sleep(1)

async def attack_6_missing_headers():
    """Attack 6: Missing Security Headers"""
    print_attack(
        "Missing Security Headers",
        "Sending webhook without required security headers"
    )
    
    payload = {
        "event": "test.event",
        "data": "test"
    }
    
    print_info("Sending webhook without X-Signature header...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/webhooks/{TEST_PROVIDER_NAME}",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5.0
            )
            
            if response.status_code == 200:
                print_error("ATTACK SUCCEEDED - Missing headers accepted!")
            else:
                print_success("ATTACK BLOCKED - Missing headers rejected")
            
            print_info(f"Response: {response.json()}\n")
        except Exception as e:
            print_error(f"Error: {str(e)}\n")
    
    await asyncio.sleep(1)

async def attack_7_future_timestamp():
    """Attack 7: Future Timestamp"""
    print_attack(
        "Future Timestamp",
        "Sending webhook with timestamp far in the future"
    )
    
    payload = {
        "event": "future.event",
        "data": "test"
    }
    
    signature = calculate_signature(payload, TEST_SECRET_KEY)
    
    # Use timestamp 1 hour in the future
    future_timestamp = (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"
    request_id = str(uuid.uuid4())
    
    print_info(f"Current time: {datetime.utcnow().isoformat()}Z")
    print_info(f"Webhook timestamp: {future_timestamp} (1 hour in future)")
    
    result = await send_webhook(payload, signature, future_timestamp, request_id)
    
    if result["success"]:
        print_error("ATTACK SUCCEEDED - Future timestamp accepted!")
    else:
        print_success("ATTACK BLOCKED - Future timestamp rejected")
    
    print_info(f"Response: {result['body']}\n")
    await asyncio.sleep(1)

async def attack_8_valid_webhook():
    """Attack 8: Valid Webhook (Control Test)"""
    print_attack(
        "Valid Webhook",
        "Sending a properly signed webhook to verify normal operation"
    )
    
    payload = {
        "event": "valid.webhook",
        "customer_id": "cust_valid",
        "amount": 250,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    signature = calculate_signature(payload, TEST_SECRET_KEY)
    timestamp = datetime.utcnow().isoformat() + "Z"
    request_id = str(uuid.uuid4())
    
    print_info(f"Payload: {json.dumps(payload)}")
    print_info(f"Signature: {signature[:32]}...")
    
    result = await send_webhook(payload, signature, timestamp, request_id)
    
    if result["success"]:
        print_success("WEBHOOK ACCEPTED - Valid signature and headers verified")
    else:
        print_error("WEBHOOK REJECTED - Valid webhook was blocked!")
    
    print_info(f"Response: {result['body']}\n")
    await asyncio.sleep(1)

async def main():
    """Main execution"""
    print_header("WebShield Attack Simulator")
    
    print(f"{Colors.YELLOW}This script demonstrates WebShield's security features by:"){Colors.ENDC}")
    print(f"{Colors.YELLOW}1. Creating a test user and provider"){Colors.ENDC}")
    print(f"{Colors.YELLOW}2. Executing 8 different attack scenarios"){Colors.ENDC}")
    print(f"{Colors.YELLOW}3. Showing how each attack is blocked or detected"){Colors.ENDC}")
    print(f"{Colors.YELLOW}4. Logging all events to the security dashboard\n"){Colors.ENDC}")
    
    print(f"{Colors.BOLD}Open the dashboard at: http://localhost:3000{Colors.ENDC}")
    print(f"{Colors.BOLD}Navigate to: Security Logs to see attacks in real-time\n{Colors.ENDC}")
    
    input(f"{Colors.YELLOW}Press Enter to start the attack simulation...{Colors.ENDC}\n")
    
    async with httpx.AsyncClient() as client:
        # Create user and provider
        token = await create_user(client)
        if not token:
            print_error("Failed to create user. Exiting.")
            return
        
        provider = await create_provider(client, token)
        if not provider:
            print_error("Failed to create provider. Exiting.")
            return
        
        print_header("Starting Attack Scenarios")
        
        # Execute attacks
        await attack_1_invalid_signature()
        await attack_2_replay_attack()
        await attack_3_rate_limiting()
        await attack_4_timestamp_tampering()
        await attack_5_payload_tampering()
        await attack_6_missing_headers()
        await attack_7_future_timestamp()
        await attack_8_valid_webhook()
        
        print_header("Attack Simulation Complete")
        
        print(f"{Colors.GREEN}{Colors.BOLD}Summary:{Colors.ENDC}")
        print(f"{Colors.GREEN}✓ All attacks were executed and logged{Colors.ENDC}")
        print(f"{Colors.GREEN}✓ Check the Security Logs dashboard to see all events{Colors.ENDC}")
        print(f"{Colors.GREEN}✓ Each attack demonstrates a different security feature{Colors.ENDC}\n")
        
        print(f"{Colors.CYAN}Dashboard URL: http://localhost:3000/security-logs{Colors.ENDC}")
        print(f"{Colors.CYAN}Webhooks Log: http://localhost:3000/webhooks/logs\n{Colors.ENDC}")

if __name__ == "__main__":
    asyncio.run(main())
