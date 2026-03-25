#!/usr/bin/env python3
"""
Attack Simulator Script - Demonstrates WebShield Security Features

This script:
1. Creates a test attacker user and provider
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
import redis.asyncio as redis
import string
import secrets

# Database imports
from app.db.session import AsyncSessionLocal
from app.db.models.user import User
from app.db.models.provider import Provider
from app.core.auth import get_password_hash
from sqlalchemy import select

# Configuration
BASE_URL = "http://localhost:8000"
TEST_PROVIDER_NAME = "attack-test-provider"
TEST_SECRET_KEY = "super_secret_key_12345"
CURRENT_PROVIDER_NAME = None  # Will be set after provider is created

# Generate random credentials for attacker user
def generate_password(length=16):
    """Generate a random password with safe characters"""
    # Use only safe characters that won't cause encoding issues
    # Alphanumeric + common safe special chars
    alphabet = string.ascii_letters + string.digits + "!@#$-_"
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

ATTACKER_USER_PASSWORD = generate_password()

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
    # Convert to JSON string with sorted keys (same as backend)
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    signature = hmac.new(
        secret.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

async def create_user(client: httpx.AsyncClient) -> tuple:
    """Create a new attacker user and return auth token + credentials"""
    # Create unique username and email based on timestamp
    timestamp = int(datetime.now().timestamp())
    attacker_username = f"attacker_{timestamp}"
    attacker_email = f"attacker_{timestamp}@test.com"
    
    print_info(f"Creating attacker user: {attacker_username}")
    
    async with AsyncSessionLocal() as session:
        # Create new user
        attacker_user = User(
            id=uuid.uuid4(),
            email=attacker_email,
            username=attacker_username,
            full_name="Attack Simulator Attacker",
            hashed_password=get_password_hash(ATTACKER_USER_PASSWORD),
            is_active=True
        )
        session.add(attacker_user)
        await session.commit()
        print_success(f"Attacker user created: {attacker_username}")
    
    # Now login via HTTP to get token using the provided client
    login_payload = {
        "username": attacker_username,
        "password": ATTACKER_USER_PASSWORD
    }
    print_info(f"Attempting login with username: {attacker_username}")
    print_info(f"Password being used: {ATTACKER_USER_PASSWORD}")
    print_info(f"Password length: {len(ATTACKER_USER_PASSWORD)}")
    
    response = await client.post(
        f"{BASE_URL}/login",
        json=login_payload
    )
    
    if response.status_code != 200:
        print_error(f"Failed to login (Status {response.status_code})")
        print_error(f"Error response: {response.text}")
        try:
            error_detail = response.json().get("detail", response.text)
            print_error(f"Error detail: {error_detail}")
        except:
            pass
        print_error(f"The attacker user was created but login failed!")
        print_error(f"Attacker username: {attacker_username}")
        print_error(f"Attacker email: {attacker_email}")
        print_error(f"Attacker password (that was attempted): {ATTACKER_USER_PASSWORD}")
        print_error(f"Please check the backend logs for more details.")
        return None, None, None, None
    
    token = response.json().get("access_token")
    print_success(f"Attacker logged in. Token: {token[:20]}...")
    
    # Return token and credentials
    return token, attacker_username, attacker_email, ATTACKER_USER_PASSWORD

async def create_provider(client: httpx.AsyncClient, token: str) -> dict:
    """Create a test provider for the attacker user"""
    global CURRENT_PROVIDER_NAME
    
    # Make provider name unique for this attacker
    timestamp = int(datetime.now().timestamp())
    provider_name = f"{TEST_PROVIDER_NAME}-{timestamp}"
    CURRENT_PROVIDER_NAME = provider_name
    
    print_info(f"Creating provider: {provider_name}")
    
    response = await client.post(
        f"{BASE_URL}/admin/providers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": provider_name,
            "secret_key": TEST_SECRET_KEY,
            "forwarding_url": "http://localhost:9000/webhook",
            "is_active": True
        }
    )
    
    if response.status_code not in [200, 201]:
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
            # Serialize payload with sorted keys for consistent signature
            payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            
            response = await client.post(
                f"{BASE_URL}/webhooks/{CURRENT_PROVIDER_NAME}",
                content=payload_json,
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

async def attack_3_rate_limiting(provider_id: str = None):
    """Attack 3: Rate Limiting Bypass"""
    print_attack(
        "Rate Limiting Bypass",
        "Sending multiple webhooks rapidly to exceed rate limits"
    )
    
    # Clear rate limit from Redis before this attack
    if provider_id:
        try:
            redis_client = await redis.from_url("redis://localhost:6379", encoding="utf-8", decode_responses=True)
            rate_limit_key = f"rate_limit:{provider_id}"
            await redis_client.delete(rate_limit_key)
            print_info(f"Cleared rate limit counter for provider")
            await redis_client.aclose()
        except Exception as e:
            print_info(f"Could not clear rate limit (Redis may not be available): {e}")
    
    print_info("Sending 15 webhooks in rapid succession ...\n")
    
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
                f"{BASE_URL}/webhooks/{CURRENT_PROVIDER_NAME}",
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
    
    print(f"{Colors.YELLOW}This script demonstrates WebShield's security features by:{Colors.ENDC}")
    print(f"{Colors.YELLOW}1. Creating a test user and provider{Colors.ENDC}")
    print(f"{Colors.YELLOW}2. Executing 8 different attack scenarios{Colors.ENDC}")
    print(f"{Colors.YELLOW}3. Showing how each attack is blocked or detected{Colors.ENDC}")
    print(f"{Colors.YELLOW}4. Logging all events to the security dashboard{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Open the dashboard at: http://localhost:3000{Colors.ENDC}")
    print(f"{Colors.BOLD}Navigate to: Security Logs to see attacks in real-time\n{Colors.ENDC}")
    
    input(f"{Colors.YELLOW}Press Enter to start the attack simulation...{Colors.ENDC}\n")
    
    async with httpx.AsyncClient() as client:
        # Create user and provider
        print_header("Setting Up Attacker Account")
        token, attacker_username, attacker_email, attacker_password = await create_user(client)
        if not token:
            print_error("FATAL: Failed to create user credentials. Cannot continue.")
            print_error("The user was created in the database but login failed.")
            print_error("Please check backend logs for authentication issues.")
            return
        
        print_success("Attacker account created and verified!")
        
        provider = await create_provider(client, token)
        if not provider:
            print_error("FATAL: Failed to create provider. Cannot continue.")
            return
        
        print_success("Provider created successfully!")
        print_header("Starting Attack Scenarios")
        
        # Execute attacks
        await attack_1_invalid_signature()
        await attack_2_replay_attack()
        await attack_3_rate_limiting(provider.get('id'))
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
        
        print(f"{Colors.BOLD}{Colors.GREEN}✅ VERIFIED LOGIN CREDENTIALS FOR ATTACKER ACCOUNT:{Colors.ENDC}")
        print(f"{Colors.BOLD}These credentials have been tested and confirmed to work!{Colors.ENDC}\n")
        print(f"{Colors.YELLOW}Username: {attacker_username}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Email: {attacker_email}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Password: {attacker_password}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Paste these exactly as shown above{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}{Colors.CYAN}DASHBOARD LINKS:{Colors.ENDC}")
        print(f"{Colors.CYAN}🔐 Login: http://localhost:3000/login{Colors.ENDC}")
        print(f"{Colors.CYAN}📊 Dashboard: http://localhost:3000/dashboard{Colors.ENDC}")
        print(f"{Colors.CYAN}🛡️  Security Logs: http://localhost:3000/security-logs{Colors.ENDC}")
        print(f"{Colors.CYAN}📨 Webhooks Log: http://localhost:3000/webhooks/logs{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}{Colors.GREEN}PROVIDER DETAILS:{Colors.ENDC}")
        print(f"{Colors.GREEN}Provider Name: {provider['name']}{Colors.ENDC}")
        print(f"{Colors.GREEN}Secret Key: {TEST_SECRET_KEY}{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}{Colors.CYAN}DEMO ACCOUNT DETAILS (To see seed data):{Colors.ENDC}")
        print(f"{Colors.CYAN}Username: demo{Colors.ENDC}")
        print(f"{Colors.CYAN}Password: demo123{Colors.ENDC}\n")

if __name__ == "__main__":
    asyncio.run(main())
