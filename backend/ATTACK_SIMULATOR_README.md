# WebShield Attack Simulator

A comprehensive attack simulation tool that demonstrates WebShield's security features by executing various attack scenarios and logging them to the security dashboard.

## Overview

The attack simulator creates a test user and provider, then executes 8 different attack scenarios to demonstrate how WebShield protects against real-world webhook security threats.

## Prerequisites

- WebShield backend running on `http://localhost:8000`
- WebShield frontend running on `http://localhost:3000`
- Python 3.8+ (for Python version) or PowerShell (for Windows version)

## Installation

### Python Version

```bash
# Install required dependencies
pip install httpx

# Make script executable (Linux/Mac)
chmod +x backend/attack_simulator.py
```

### PowerShell Version

No additional dependencies required. Works on Windows, Mac, and Linux with PowerShell 7+.

## Usage

### Python Version

```bash
# Run from backend directory
python attack_simulator.py

# Or from project root
python backend/attack_simulator.py
```

### PowerShell Version

```powershell
# Run from backend directory
.\attack_simulator.ps1

# Or from project root
.\backend\attack_simulator.ps1
```

## Attack Scenarios

The simulator executes 8 different attack scenarios:

### 1. **Invalid Signature Attack**
- **What it tests**: HMAC-SHA256 signature verification
- **Attack method**: Sends webhook with tampered signature
- **Expected result**: Request blocked with "Invalid signature" error
- **Security feature**: Constant-time HMAC comparison

### 2. **Replay Attack**
- **What it tests**: Replay attack prevention using Redis deduplication
- **Attack method**: Resends the same webhook with identical request ID
- **Expected result**: First request accepted, second request blocked
- **Security feature**: Request ID deduplication with TTL

### 3. **Rate Limiting Bypass**
- **What it tests**: Token bucket rate limiting algorithm
- **Attack method**: Sends 15 webhooks rapidly (limit is 10/minute)
- **Expected result**: First 10 accepted, remaining blocked
- **Security feature**: Per-provider rate limiting

### 4. **Timestamp Tampering**
- **What it tests**: Timestamp validation and freshness checking
- **Attack method**: Sends webhook with timestamp 10 minutes old
- **Expected result**: Request blocked with "Timestamp too old" error
- **Security feature**: Configurable timestamp window (default 5 minutes)

### 5. **Payload Tampering**
- **What it tests**: Payload integrity checking with SHA256 hashing
- **Attack method**: Modifies payload after signature calculation
- **Expected result**: Request blocked with "Payload tampering detected" error
- **Security feature**: SHA256 payload hash verification

### 6. **Missing Security Headers**
- **What it tests**: Required header validation
- **Attack method**: Sends webhook without X-Signature header
- **Expected result**: Request blocked with "Missing required headers" error
- **Security feature**: Header presence validation

### 7. **Future Timestamp Attack**
- **What it tests**: Timestamp validation for future dates
- **Attack method**: Sends webhook with timestamp 1 hour in the future
- **Expected result**: Request blocked with "Timestamp too far in future" error
- **Security feature**: Timestamp boundary validation

### 8. **Valid Webhook (Control Test)**
- **What it tests**: Normal webhook processing
- **Attack method**: Sends properly signed webhook with valid headers
- **Expected result**: Request accepted and processed
- **Security feature**: Validates that legitimate webhooks work correctly

## Viewing Results

### Real-Time Dashboard

1. Open http://localhost:3000 in your browser
2. Navigate to **Security Logs** tab
3. Watch attacks appear in real-time as the simulator runs
4. Each attack is logged with:
   - Event type (e.g., "invalid_signature", "replay_attempt")
   - Provider name
   - Timestamp
   - IP address
   - Request details

### Webhooks Log

1. Navigate to **Webhooks** tab
2. View all webhook events (both successful and failed)
3. Expand each event to see:
   - Payload
   - Headers
   - Signature verification status
   - Payload hash

### Security Events Breakdown

The simulator generates the following security events:

| Event Type | Count | Description |
|-----------|-------|-------------|
| `invalid_signature` | 1 | Signature verification failed |
| `replay_attempt` | 1 | Duplicate request ID detected |
| `rate_limit_exceeded` | 5 | Rate limit threshold exceeded |
| `timestamp_too_old` | 1 | Timestamp outside valid window |
| `payload_tampering_detected` | 1 | Payload hash mismatch |
| `missing_headers` | 1 | Required headers missing |
| `timestamp_too_far_future` | 1 | Timestamp in future |
| `webhook_received` | 1 | Valid webhook accepted |

**Total: 12 security events logged**

## Output Example

```
======================================================================
                    WebShield Attack Simulator
======================================================================

This script demonstrates WebShield's security features by:
1. Creating a test user and provider
2. Executing 8 different attack scenarios
3. Showing how each attack is blocked or detected
4. Logging all events to the security dashboard

Open the dashboard at: http://localhost:3000
Navigate to: Security Logs to see attacks in real-time

Press Enter to start the attack simulation...

ℹ Creating user: attacker@test.com
✓ User created and logged in. Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
ℹ Creating provider: attack-test-provider
✓ Provider created: 550e8400-e29b-41d4-a716-446655440000

======================================================================
                      Starting Attack Scenarios
======================================================================

🔥 ATTACK: Invalid Signature
   Sending webhook with tampered signature to bypass HMAC verification

ℹ Correct signature: 0123456789abcdef...
ℹ Tampered signature: 0000000000000000...
✓ ATTACK BLOCKED - Invalid signature rejected
ℹ Response: {"detail":"Invalid signature"}

...
```

## Customization

### Modify Attack Parameters

Edit the configuration at the top of the script:

```python
# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "attacker@test.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_PROVIDER_NAME = "attack-test-provider"
TEST_SECRET_KEY = "super_secret_key_12345"
```

### Add Custom Attacks

Add new attack functions following the pattern:

```python
async def attack_9_custom_attack():
    """Attack 9: Custom Attack"""
    print_attack(
        "Custom Attack Name",
        "Description of what this attack tests"
    )
    
    # Your attack implementation here
    
    print_success("ATTACK BLOCKED - Custom protection worked")
```

## Security Implications

This simulator demonstrates that WebShield provides:

✅ **Signature Verification**: HMAC-SHA256 with constant-time comparison
✅ **Replay Protection**: Request ID deduplication with Redis
✅ **Rate Limiting**: Token bucket algorithm per provider
✅ **Timestamp Validation**: Configurable time window validation
✅ **Payload Integrity**: SHA256 hash verification
✅ **Header Validation**: Required header presence checking
✅ **Comprehensive Logging**: All security events logged for audit trails

## Troubleshooting

### Connection Refused

```
Error: Connection refused
```

**Solution**: Ensure backend is running on port 8000:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### User Already Exists

```
Error: User already exists
```

**Solution**: Change `TEST_USER_EMAIL` in the script or delete the user from the database.

### Provider Not Found

```
Error: Provider 'attack-test-provider' not found
```

**Solution**: Ensure the provider was created successfully. Check the output for errors.

### WebSocket Connection Issues

If you don't see real-time updates:

1. Check that frontend is running on port 3000
2. Verify WebSocket connection in browser console
3. Refresh the page to reconnect

## Performance Notes

- Each attack takes ~1 second to execute
- Total simulation time: ~10 seconds
- All events are logged to PostgreSQL
- WebSocket broadcasts events in real-time
- No impact on production systems

## Next Steps

After running the simulator:

1. **Review Security Logs**: Analyze how each attack was detected
2. **Check Webhook Events**: See the full payload and headers
3. **Export Reports**: Use the dashboard to export PDF/CSV reports
4. **Customize Rules**: Create alert rules for specific attack patterns
5. **Monitor Trends**: Track security events over time

## Support

For issues or questions:

1. Check the WebShield README.md
2. Review the test files: `test_all_functionality.py`, `test_adversarial_security.py`
3. Check backend logs: `docker logs webshield-backend`
4. Check frontend console: Browser DevTools → Console tab

## License

Part of the WebShield project. See LICENSE file for details.
