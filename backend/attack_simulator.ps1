#!/usr/bin/env pwsh
<#
.SYNOPSIS
    WebShield Attack Simulator - Demonstrates security features
    
.DESCRIPTION
    This script creates a test user and provider, then executes various attack scenarios
    to demonstrate WebShield's security capabilities.
    
.EXAMPLE
    .\attack_simulator.ps1
#>

# Configuration
$BASE_URL = "http://localhost:8000"
$TEST_USER_EMAIL = "attacker@test.com"
$TEST_USER_PASSWORD = "TestPassword123!"
$TEST_PROVIDER_NAME = "attack-test-provider"
$TEST_SECRET_KEY = "super_secret_key_12345"

# Helper functions
function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Magenta
    Write-Host $Text.PadLeft(35 + $Text.Length / 2) -ForegroundColor Magenta -BackgroundColor Black
    Write-Host ("=" * 70) -ForegroundColor Magenta
    Write-Host ""
}

function Write-Attack {
    param([string]$Name, [string]$Description)
    Write-Host "🔥 ATTACK: $Name" -ForegroundColor Cyan -BackgroundColor Black
    Write-Host "   $Description" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Blue
}

function Calculate-Signature {
    param([hashtable]$Payload, [string]$Secret)
    
    $json = $Payload | ConvertTo-Json -Compress
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
    $secretBytes = [System.Text.Encoding]::UTF8.GetBytes($Secret)
    
    $hmac = New-Object System.Security.Cryptography.HMACSHA256
    $hmac.Key = $secretBytes
    $hash = $hmac.ComputeHash($bytes)
    
    return ($hash | ForEach-Object { $_.ToString("x2") }) -join ""
}

function Create-User {
    Write-Info "Creating user: $TEST_USER_EMAIL"
    
    try {
        # Create user
        $signupResponse = Invoke-RestMethod -Uri "$BASE_URL/signup" -Method Post -ContentType "application/json" -Body @{
            email = $TEST_USER_EMAIL
            password = $TEST_USER_PASSWORD
            username = "attacker_test"
        } | ConvertTo-Json
        
        # Login
        $loginResponse = Invoke-RestMethod -Uri "$BASE_URL/login" -Method Post -ContentType "application/json" -Body @{
            email = $TEST_USER_EMAIL
            password = $TEST_USER_PASSWORD
        } | ConvertTo-Json
        
        $token = ($loginResponse | ConvertFrom-Json).access_token
        Write-Success "User created and logged in. Token: $($token.Substring(0, 20))..."
        return $token
    }
    catch {
        Write-Error-Custom "Failed to create user: $_"
        return $null
    }
}

function Create-Provider {
    param([string]$Token)
    
    Write-Info "Creating provider: $TEST_PROVIDER_NAME"
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/admin/providers" -Method Post `
            -Headers @{"Authorization" = "Bearer $Token"} `
            -ContentType "application/json" `
            -Body @{
                name = $TEST_PROVIDER_NAME
                secret_key = $TEST_SECRET_KEY
                forwarding_url = "http://localhost:9000/webhook"
                is_active = $true
            } | ConvertTo-Json
        
        $provider = $response | ConvertFrom-Json
        Write-Success "Provider created: $($provider.id)"
        return $provider
    }
    catch {
        Write-Error-Custom "Failed to create provider: $_"
        return $null
    }
}

function Send-Webhook {
    param(
        [hashtable]$Payload,
        [string]$Signature,
        [string]$Timestamp,
        [string]$RequestId
    )
    
    $headers = @{
        "Content-Type" = "application/json"
    }
    
    if ($Signature) { $headers["X-Signature"] = $Signature }
    if ($Timestamp) { $headers["X-Timestamp"] = $Timestamp }
    if ($RequestId) { $headers["X-Request-ID"] = $RequestId }
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/webhooks/$TEST_PROVIDER_NAME" `
            -Method Post `
            -Headers $headers `
            -ContentType "application/json" `
            -Body ($Payload | ConvertTo-Json)
        
        return @{
            StatusCode = 200
            Body = $response
            Success = $true
        }
    }
    catch {
        return @{
            StatusCode = 0
            Body = @{ error = $_.Exception.Message }
            Success = $false
        }
    }
}

function Attack-InvalidSignature {
    Write-Attack "Invalid Signature" "Sending webhook with tampered signature to bypass HMAC verification"
    
    $payload = @{
        event = "payment.completed"
        amount = 1000
        customer_id = "cust_123"
    }
    
    $correctSig = Calculate-Signature $payload $TEST_SECRET_KEY
    $tamperedSig = "0" * 64
    
    $timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $requestId = [guid]::NewGuid().ToString()
    
    Write-Info "Correct signature: $($correctSig.Substring(0, 16))..."
    Write-Info "Tampered signature: $($tamperedSig.Substring(0, 16))..."
    
    $result = Send-Webhook $payload $tamperedSig $timestamp $requestId
    
    if ($result.Success) {
        Write-Error-Custom "ATTACK SUCCEEDED - Signature validation failed!"
    } else {
        Write-Success "ATTACK BLOCKED - Invalid signature rejected"
    }
    
    Write-Info "Response: $($result.Body | ConvertTo-Json -Compress)"
    Write-Host ""
    Start-Sleep -Seconds 1
}

function Attack-ReplayAttack {
    Write-Attack "Replay Attack" "Resending the same webhook multiple times to bypass replay protection"
    
    $payload = @{
        event = "order.created"
        order_id = "ord_456"
        amount = 500
    }
    
    $signature = Calculate-Signature $payload $TEST_SECRET_KEY
    $timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $requestId = [guid]::NewGuid().ToString()
    
    Write-Info "Sending webhook with request_id: $requestId"
    
    $result1 = Send-Webhook $payload $signature $timestamp $requestId
    Write-Info "First attempt: $($result1.Body | ConvertTo-Json -Compress)"
    
    Start-Sleep -Milliseconds 500
    
    Write-Info "Replaying the same request..."
    $result2 = Send-Webhook $payload $signature $timestamp $requestId
    
    if ($result2.Success) {
        Write-Error-Custom "ATTACK SUCCEEDED - Replay protection failed!"
    } else {
        Write-Success "ATTACK BLOCKED - Replay attempt detected and rejected"
    }
    
    Write-Info "Response: $($result2.Body | ConvertTo-Json -Compress)"
    Write-Host ""
    Start-Sleep -Seconds 1
}

function Attack-RateLimiting {
    Write-Attack "Rate Limiting Bypass" "Sending multiple webhooks rapidly to exceed rate limits"
    
    Write-Info "Sending 15 webhooks in rapid succession (limit is 10/minute)..."
    Write-Host ""
    
    $blockedCount = 0
    $successCount = 0
    
    for ($i = 0; $i -lt 15; $i++) {
        $payload = @{
            event = "test.event.$i"
            sequence = $i
        }
        
        $signature = Calculate-Signature $payload $TEST_SECRET_KEY
        $timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        $requestId = [guid]::NewGuid().ToString()
        
        $result = Send-Webhook $payload $signature $timestamp $requestId
        
        if ($result.Success) {
            $successCount++
            Write-Info "  Request $($i+1): ✓ Accepted"
        } else {
            $blockedCount++
            Write-Error-Custom "  Request $($i+1): ✗ Blocked - $($result.Body.detail)"
        }
        
        Start-Sleep -Milliseconds 100
    }
    
    Write-Host ""
    if ($blockedCount -gt 0) {
        Write-Success "ATTACK BLOCKED - Rate limiting enforced ($blockedCount requests blocked)"
    } else {
        Write-Error-Custom "ATTACK SUCCEEDED - No rate limiting detected ($successCount requests accepted)"
    }
    
    Write-Info "Accepted: $successCount, Blocked: $blockedCount"
    Write-Host ""
    Start-Sleep -Seconds 1
}

function Attack-TimestampTampering {
    Write-Attack "Timestamp Tampering" "Sending webhook with old timestamp to bypass timestamp validation"
    
    $payload = @{
        event = "user.created"
        user_id = "usr_789"
    }
    
    $signature = Calculate-Signature $payload $TEST_SECRET_KEY
    $oldTimestamp = (Get-Date).ToUniversalTime().AddMinutes(-10).ToString("yyyy-MM-ddTHH:mm:ssZ")
    $requestId = [guid]::NewGuid().ToString()
    
    Write-Info "Current time: $((Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"))"
    Write-Info "Webhook timestamp: $oldTimestamp (10 minutes old)"
    
    $result = Send-Webhook $payload $signature $oldTimestamp $requestId
    
    if ($result.Success) {
        Write-Error-Custom "ATTACK SUCCEEDED - Old timestamp accepted!"
    } else {
        Write-Success "ATTACK BLOCKED - Old timestamp rejected"
    }
    
    Write-Info "Response: $($result.Body | ConvertTo-Json -Compress)"
    Write-Host ""
    Start-Sleep -Seconds 1
}

function Attack-PayloadTampering {
    Write-Attack "Payload Tampering" "Modifying payload after signature calculation to bypass integrity check"
    
    $originalPayload = @{
        event = "payment.completed"
        amount = 100
        customer_id = "cust_999"
    }
    
    $signature = Calculate-Signature $originalPayload $TEST_SECRET_KEY
    
    $tamperedPayload = @{
        event = "payment.completed"
        amount = 10000
        customer_id = "cust_999"
    }
    
    $timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $requestId = [guid]::NewGuid().ToString()
    
    Write-Info "Original payload: $($originalPayload | ConvertTo-Json -Compress)"
    Write-Info "Tampered payload: $($tamperedPayload | ConvertTo-Json -Compress)"
    Write-Info "Signature calculated for original payload"
    
    $result = Send-Webhook $tamperedPayload $signature $timestamp $requestId
    
    if ($result.Success) {
        Write-Error-Custom "ATTACK SUCCEEDED - Payload tampering not detected!"
    } else {
        Write-Success "ATTACK BLOCKED - Payload tampering detected"
    }
    
    Write-Info "Response: $($result.Body | ConvertTo-Json -Compress)"
    Write-Host ""
    Start-Sleep -Seconds 1
}

function Attack-MissingHeaders {
    Write-Attack "Missing Security Headers" "Sending webhook without required security headers"
    
    $payload = @{
        event = "test.event"
        data = "test"
    }
    
    Write-Info "Sending webhook without X-Signature header..."
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/webhooks/$TEST_PROVIDER_NAME" `
            -Method Post `
            -Headers @{"Content-Type" = "application/json"} `
            -ContentType "application/json" `
            -Body ($payload | ConvertTo-Json)
        
        Write-Error-Custom "ATTACK SUCCEEDED - Missing headers accepted!"
        Write-Info "Response: $($response | ConvertTo-Json -Compress)"
    }
    catch {
        Write-Success "ATTACK BLOCKED - Missing headers rejected"
        Write-Info "Response: $($_.Exception.Message)"
    }
    
    Write-Host ""
    Start-Sleep -Seconds 1
}

function Attack-FutureTimestamp {
    Write-Attack "Future Timestamp" "Sending webhook with timestamp far in the future"
    
    $payload = @{
        event = "future.event"
        data = "test"
    }
    
    $signature = Calculate-Signature $payload $TEST_SECRET_KEY
    $futureTimestamp = (Get-Date).ToUniversalTime().AddHours(1).ToString("yyyy-MM-ddTHH:mm:ssZ")
    $requestId = [guid]::NewGuid().ToString()
    
    Write-Info "Current time: $((Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"))"
    Write-Info "Webhook timestamp: $futureTimestamp (1 hour in future)"
    
    $result = Send-Webhook $payload $signature $futureTimestamp $requestId
    
    if ($result.Success) {
        Write-Error-Custom "ATTACK SUCCEEDED - Future timestamp accepted!"
    } else {
        Write-Success "ATTACK BLOCKED - Future timestamp rejected"
    }
    
    Write-Info "Response: $($result.Body | ConvertTo-Json -Compress)"
    Write-Host ""
    Start-Sleep -Seconds 1
}

function Attack-ValidWebhook {
    Write-Attack "Valid Webhook" "Sending a properly signed webhook to verify normal operation"
    
    $payload = @{
        event = "valid.webhook"
        customer_id = "cust_valid"
        amount = 250
        timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss")
    }
    
    $signature = Calculate-Signature $payload $TEST_SECRET_KEY
    $timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $requestId = [guid]::NewGuid().ToString()
    
    Write-Info "Payload: $($payload | ConvertTo-Json -Compress)"
    Write-Info "Signature: $($signature.Substring(0, 32))..."
    
    $result = Send-Webhook $payload $signature $timestamp $requestId
    
    if ($result.Success) {
        Write-Success "WEBHOOK ACCEPTED - Valid signature and headers verified"
    } else {
        Write-Error-Custom "WEBHOOK REJECTED - Valid webhook was blocked!"
    }
    
    Write-Info "Response: $($result.Body | ConvertTo-Json -Compress)"
    Write-Host ""
    Start-Sleep -Seconds 1
}

# Main execution
Write-Header "WebShield Attack Simulator"

Write-Host "This script demonstrates WebShield's security features by:" -ForegroundColor Yellow
Write-Host "1. Creating a test user and provider" -ForegroundColor Yellow
Write-Host "2. Executing 8 different attack scenarios" -ForegroundColor Yellow
Write-Host "3. Showing how each attack is blocked or detected" -ForegroundColor Yellow
Write-Host "4. Logging all events to the security dashboard" -ForegroundColor Yellow
Write-Host ""

Write-Host "Open the dashboard at: http://localhost:3000" -ForegroundColor Cyan -BackgroundColor Black
Write-Host "Navigate to: Security Logs to see attacks in real-time" -ForegroundColor Cyan -BackgroundColor Black
Write-Host ""

Read-Host "Press Enter to start the attack simulation"
Write-Host ""

# Create user and provider
$token = Create-User
if (-not $token) {
    Write-Error-Custom "Failed to create user. Exiting."
    exit 1
}

$provider = Create-Provider $token
if (-not $provider) {
    Write-Error-Custom "Failed to create provider. Exiting."
    exit 1
}

Write-Header "Starting Attack Scenarios"

# Execute attacks
Attack-InvalidSignature
Attack-ReplayAttack
Attack-RateLimiting
Attack-TimestampTampering
Attack-PayloadTampering
Attack-MissingHeaders
Attack-FutureTimestamp
Attack-ValidWebhook

Write-Header "Attack Simulation Complete"

Write-Host "Summary:" -ForegroundColor Green -BackgroundColor Black
Write-Host "✓ All attacks were executed and logged" -ForegroundColor Green
Write-Host "✓ Check the Security Logs dashboard to see all events" -ForegroundColor Green
Write-Host "✓ Each attack demonstrates a different security feature" -ForegroundColor Green
Write-Host ""

Write-Host "Dashboard URL: http://localhost:3000/security-logs" -ForegroundColor Cyan
Write-Host "Webhooks Log: http://localhost:3000/webhooks/logs" -ForegroundColor Cyan
Write-Host ""
