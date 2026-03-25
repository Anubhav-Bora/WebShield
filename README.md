# 🛡️ WebShield - Advanced Webhook Security & Attack Simulation Platform

A comprehensive, production-ready webhook security platform with real-time event streaming, advanced security features, and attack simulation capabilities for testing webhook resilience.

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Node.js](https://img.shields.io/badge/Node.js-18+-green)
![Status](https://img.shields.io/badge/status-Active-brightgreen)

---

## 📋 Table of Contents

- [Overview](#overview)
- [✨ Key Features](#key-features)
- [🏗️ Tech Stack](#tech-stack)
- [🚀 Quick Start](#quick-start)
- [⚙️ Configuration](#configuration)
- [📖 Usage Guide](#usage-guide)
- [🔧 Scripts & Commands](#scripts--commands)
- [🏛️ Project Structure](#project-structure)
- [🔐 Security Features](#security-features)
- [📊 Dashboard Features](#dashboard-features)
- [🎯 Attack Simulator](#attack-simulator)
- [📡 API Endpoints](#api-endpoints)
- [🐛 Troubleshooting](#troubleshooting)

---

## 📝 Overview

**WebShield** is a sophisticated webhook management and security testing platform designed to help development teams:

- 🎯 **Manage webhooks** across multiple providers with granular permission control
- 🔍 **Monitor events** in real-time with WebSocket streaming
- 🚨 **Detect security threats** through advanced payload analysis and rate limiting
- 🧪 **Simulate attacks** to test webhook endpoints under various security scenarios
- 📊 **Analyze patterns** with comprehensive analytics and audit logging
- 🔐 **Enforce security** through JWT authentication, CSRF protection, and payload integrity verification

Perfect for testing webhook resilience, understanding attack patterns, and building secure webhook ecosystems.

---

## ✨ Key Features

### 🔐 Security
- **JWT Authentication** with secure token-based access control
- **CSRF Protection** on all state-changing operations
- **Payload Integrity Verification** using HMAC signatures
- **Rate Limiting** with Redis-backed sliding window algorithm
- **Security Headers** enforcement (HSTS, X-Frame-Options, CSP, etc.)
- **Password Hashing** using Argon2 via passlib
- **SQL Injection Prevention** through parameterized queries

### 📡 Real-time Features
- **WebSocket Streaming** for instant event notifications
- **Live Updates** on webhook events, security alerts, and statistics
- **Connection Management** with automatic reconnection and exponential backoff
- **Multi-user Support** with per-user connection tracking

### 📊 Monitoring & Analytics
- **Real-time Dashboard** with animated charts and stats
- **Webhook Event Tracking** with payload inspection
- **Security Logs** with detailed threat information
- **Analytics** on event patterns, success rates, and response times
- **Audit Logging** for compliance and debugging
- **Provider Analytics** showing per-provider statistics

### 🎯 Webhook Management
- **Multi-provider Support** (HTTP, HTTPS, custom protocols)
- **Provider Isolation** - each user sees only their providers
- **Event Routing** based on provider configuration
- **Retry Logic** with exponential backoff for failed events
- **Timeout Handling** for slow webhook endpoints
- **Payload Formatting** with custom headers and authentication

### 🧪 Attack Simulation
- **8 Attack Scenarios**:
  1. ✅ Normal Event (baseline)
  2. 🔴 Missing Signature Attack
  3. ⚠️ Invalid Signature Attack
  4. 💥 Large Payload Attack
  5. 📢 Verbose Event Attack
  6. 🔁 Duplicate Event Attack
  7. 🕐 Delayed Event Attack
  8. 🧬 Malformed JSON Attack

- **Automatic User Creation** with verified credentials
- **Provider Simulation** with realistic test data
- **Detailed Reporting** on attack results

### 📈 Analytics & Insights
- **Time-series Analytics** for event trends
- **Provider Performance** metrics
- **Success/Failure Rates** with detailed breakdowns
- **Response Time Analysis**
- **Attack Pattern Detection**

---

## 🏗️ Tech Stack

### 🖥️ Backend
| Technology | Purpose | Version |
|------------|---------|---------|
| ![FastAPI](https://img.shields.io/badge/FastAPI-009688) | Web Framework | 0.104+ |
| ![Python](https://img.shields.io/badge/Python-3776AB) | Language | 3.11+ |
| ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-FF7D00) | ORM | 2.0+ |
| ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791) | Database | 14+ |
| ![Redis](https://img.shields.io/badge/Redis-DC382D) | Caching/Rate Limiting | 7.0+ |
| ![Uvicorn](https://img.shields.io/badge/Uvicorn-000000) | ASGI Server | 0.24+ |
| ![Pydantic](https://img.shields.io/badge/Pydantic-E92063) | Data Validation | 2.0+ |
| ![httpx](https://img.shields.io/badge/httpx-009688) | Async HTTP | 0.24+ |
| ![Alembic](https://img.shields.io/badge/Alembic-FF7D00) | Migrations | 1.12+ |

### 🎨 Frontend
| Technology | Purpose | Version |
|------------|---------|---------|
| ![Next.js](https://img.shields.io/badge/Next.js-000000) | Framework | 16.1+ |
| ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6) | Language | 5.0+ |
| ![Tailwind CSS](https://img.shields.io/badge/Tailwind-38B2AC) | Styling | 3.3+ |
| ![React Query](https://img.shields.io/badge/React%20Query-FF4154) | State Mgmt | 4.35+ |
| ![Zustand](https://img.shields.io/badge/Zustand-15AAD7) | Store | 4.4+ |
| ![Axios](https://img.shields.io/badge/Axios-5A29E4) | HTTP Client | 1.6+ |
| ![Shadcn/ui](https://img.shields.io/badge/Shadcn%2Fui-000000) | UI Components | Latest |
| ![GSAP](https://img.shields.io/badge/GSAP-88CE02) | Animations | 3.12+ |

### 🐳 DevOps & Tools
| Tool | Purpose |
|------|---------|
| ![Docker](https://img.shields.io/badge/Docker-2496ED) | Containerization |
| ![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2496ED) | Orchestration |
| ![Git](https://img.shields.io/badge/Git-F05032) | Version Control |
| ![Postman](https://img.shields.io/badge/Postman-FF6C37) | API Testing |

---

## 🚀 Quick Start

### Prerequisites
- ![Python](https://img.shields.io/badge/Python-3.11+-blue) Python 3.11 or higher
- ![Node.js](https://img.shields.io/badge/Node.js-18+-green) Node.js 18 or higher
- ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue) PostgreSQL 14 or higher
- ![Redis](https://img.shields.io/badge/Redis-7.0+-red) Redis 7.0 or higher
- ![Docker](https://img.shields.io/badge/Docker-required-blue) Docker & Docker Compose (optional but recommended)

### Installation

#### 1️⃣ Clone Repository
```bash
git clone https://github.com/your-org/webshield.git
cd webshield
```

#### 2️⃣ Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration
```

#### 3️⃣ Database Setup
```bash
# Run migrations
alembic upgrade head

# Create demo user (optional)
python create_demo_user.py
```

#### 4️⃣ Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install
# or
yarn install

# Start development server
npm run dev
```

#### 5️⃣ Start Services
```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Using Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/webshield

# Redis
REDIS_URL=redis://localhost:6380

# JWT
SECRET_KEY=your-super-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_RESET_SECONDS=60

# Server
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Database Configuration
The application uses PostgreSQL with SQLAlchemy async ORM. Migrations are managed with Alembic.

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 📖 Usage Guide

### 🏨 Web Interface Access

1. **Open Dashboard**: Navigate to `http://localhost:3000`
2. **Create Account**: Sign up with email and password
3. **Set Providers**: Add webhook providers to monitor
4. **View Analytics**: Watch real-time events and statistics

### 👤 User Roles

- **Standard User**: Can manage own providers and webhooks
- **Demo User**: Pre-configured with sample providers (demo/demo123)
- **Attacker User**: Created for attack simulation testing

### 🔑 Demo Login
```
Username: demo
Password: demo123
```

This user comes pre-configured with sample providers and seed data.

---

## 🔧 Scripts & Commands

### Backend Scripts

#### 1️⃣ Attack Simulator
Simulates 8 different attack scenarios against your webhook endpoints.

```bash
cd backend

# Run attack simulator
python attack_simulator.py
```

**Output Example:**
```
======================================================================
                     Setting Up Attacker Account
======================================================================

ℹ Creating attacker user: attacker_1774427547
✓ Attacker user created: attacker_1774427547
ℹ Attempting login with username: attacker_1774427547
ℹ Password being used: _n5jsbvyS1mORX0f
ℹ Password length: 16
✓ Attacker logged in. Token: eyJhbGciOiJIUzI1NiIs...
✓ Attacker account created and verified!
ℹ Creating provider: attack-test-provider-1774427549
✓ Provider created: 76eeaf42-e70b-41e8-b9a6-923f381517ed
✓ Provider created successfully!

======================================================================
                      Starting Attack Scenarios
======================================================================

🔥 ATTACK: Invalid Signature
   Sending webhook with tampered signature to bypass HMAC verification

ℹ Correct signature: 283fdd9a76ea9e11...
ℹ Tampered signature: 0000000000000000...
✓ ATTACK BLOCKED - Invalid signature rejected
ℹ Response: {'detail': 'Invalid webhook signature'}

🔥 ATTACK: Replay Attack
   Resending the same webhook multiple times to bypass replay protection

ℹ Sending webhook with request_id: 6ea1b850-343d-4da8-af0c-c63f37c7b0a6
ℹ First attempt: {'status': 'accepted', 'message': 'Webhook received and queued...'}
ℹ Replaying the same request...
✓ ATTACK BLOCKED - Replay attempt detected and rejected
ℹ Response: {'detail': 'Webhook already processed (replay detected)'}

🔥 ATTACK: Rate Limiting Bypass
   Sending multiple webhooks rapidly to exceed rate limits

ℹ Cleared rate limit counter for provider
ℹ Sending 15 webhooks in rapid succession...

ℹ   Request 1: ✓ Accepted
ℹ   Request 2: ✓ Accepted
ℹ   Request 3: ✓ Accepted
ℹ   Request 4: ✓ Accepted
ℹ   Request 5: ✓ Accepted
ℹ   Request 6: ✓ Accepted
ℹ   Request 7: ✓ Accepted
✗   Request 8: ✗ Blocked - Rate limit exceeded. Reset in 47 seconds
✗   Request 9: ✗ Blocked - Rate limit exceeded. Reset in 46 seconds
... (8 requests blocked)

✓ ATTACK BLOCKED - Rate limiting enforced (8 requests blocked)
ℹ Accepted: 7, Blocked: 8

🔥 ATTACK: Timestamp Tampering
🔥 ATTACK: Payload Tampering
🔥 ATTACK: Missing Security Headers
🔥 ATTACK: Future Timestamp
🔥 ATTACK: Valid Webhook

======================================================================
                      Attack Simulation Complete
======================================================================

Summary:
✓ All attacks were executed and logged
✓ Check the Security Logs dashboard to see all events
✓ Each attack demonstrates a different security feature

✅ VERIFIED LOGIN CREDENTIALS FOR ATTACKER ACCOUNT:
These credentials have been tested and confirmed to work!

Username: attacker_1774427547
Email: attacker_1774427547@test.com
Password: _n5jsbvyS1mORX0f
Paste these exactly as shown above

DASHBOARD LINKS:
🔐 Login: http://localhost:3000/login
📊 Dashboard: http://localhost:3000/dashboard
🛡️  Security Logs: http://localhost:3000/security-logs
📨 Webhooks Log: http://localhost:3000/webhooks/logs

PROVIDER DETAILS:
Provider Name: attack-test-provider-1774427549
Secret Key: super_secret_key_12345

DEMO ACCOUNT DETAILS (To see seed data):
Username: demo
Password: demo123
```

**What it does:**
- Creates a unique attacker user with verified login credentials
- Generates test providers with realistic configurations
- Executes 8 different attack scenarios demonstrating security features
- Shows real-time attack blocking and detection
- Displays all credentials and dashboard links for immediate access
- Reports detailed attack results and metrics

---

#### 2️⃣ Demo User Setup
Pre-configures demo account with sample providers.

```bash
cd backend

# Create demo user with seed providers
python create_demo_user.py
```

**Credentials:**
- Username: `demo`
- Password: `demo123`
- Pre-configured Providers: Yahoo Mail, Microsoft Graph, Slack

---

#### 3️⃣ Seed Analytics Data
Generates sample webhook events for testing analytics.

```bash
cd backend

python seed_analytics.py
```

---

#### 4️⃣ Test Scripts (Diagnostic)

##### Test Specific Credentials
```bash
python test_specific_credentials.py
```

##### Test All Logins
```bash
python test_all_logins.py
```

##### Test Password Hashing
```bash
python test_password.py
```

##### Diagnose Login Issues
```bash
python diagnose_login.py "username" "password"
```

---

### Frontend Commands

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm run start

# Linting
npm run lint

# Type checking
npm run type-check

# Format code
npm run format
```

---

## 🏛️ Project Structure

```
webshield/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── main.py                  # Application entry point
│   │   ├── api/
│   │   │   └── routes/              # API route handlers
│   │   │       ├── auth.py          # Authentication endpoints
│   │   │       ├── webhooks.py      # Webhook management
│   │   │       ├── providers.py     # Provider configuration
│   │   │       ├── websocket.py     # WebSocket endpoint
│   │   │       ├── analytics.py     # Analytics endpoints
│   │   │       └── logs.py          # Logging endpoints
│   │   ├── core/                    # Core functionality
│   │   │   ├── auth.py              # Authentication logic
│   │   │   ├── security.py          # Security utilities
│   │   │   ├── rate_limit.py        # Rate limiting
│   │   │   ├── websocket_manager.py # WebSocket management
│   │   │   ├── audit_logger.py      # Audit logging
│   │   │   ├── payload_integrity.py # HMAC verification
│   │   │   ├── security_headers.py  # Security headers
│   │   │   ├── security_logger.py   # Security event logging
│   │   │   └── alert_monitor.py     # Alert detection
│   │   ├── db/
│   │   │   ├── base.py              # Base configurations
│   │   │   ├── session.py           # Database session
│   │   │   └── models/              # SQLAlchemy models
│   │   │       ├── user.py
│   │   │       ├── provider.py
│   │   │       ├── webhook.py
│   │   │       ├── audit_log.py
│   │   │       └── security_log.py
│   │   └── schemas/                 # Pydantic schemas
│   │       ├── user.py
│   │       ├── provider.py
│   │       ├── webhook.py
│   │       └── alert.py
│   ├── alembic/                     # Database migrations
│   │   └── versions/                # Migration files
│   ├── attack_simulator.py          # Attack simulation script
│   ├── create_demo_user.py          # Demo user setup
│   ├── seed_analytics.py            # Sample data generation
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment template
│   └── mypy.ini                     # Type checking config
│
├── frontend/                        # Next.js Frontend
│   ├── src/
│   │   ├── app/                    # App routes
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx            # Home page
│   │   │   ├── login/              # Login page
│   │   │   ├── signup/             # Signup page
│   │   │   ├── dashboard/          # Main dashboard
│   │   │   ├── admin/             # Admin pages
│   │   │   ├── webhooks/          # Webhook pages
│   │   │   ├── providers/         # Provider pages
│   │   │   ├── security-logs/     # Security logs
│   │   │   └── middleware.ts      # Auth middleware
│   │   ├── components/
│   │   │   ├── layout/            # Layout components
│   │   │   └── ui/                # UI components
│   │   ├── services/              # API services
│   │   │   ├── api.ts             # Axios instance
│   │   │   ├── auth.ts            # Auth service
│   │   │   ├── webhooks.ts        # Webhook service
│   │   │   ├── providers.ts       # Provider service
│   │   │   └── export.ts          # Export service
│   │   ├── hooks/                 # Custom hooks
│   │   │   ├── useWebSocket.ts    # WebSocket hook
│   │   │   ├── useProviders.ts    # Providers hook
│   │   │   └── useWebhooks.ts     # Webhooks hook
│   │   ├── store/                 # Zustand stores
│   │   │   ├── useAuthStore.ts    # Auth state
│   │   │   └── useNotificationStore.ts
│   │   ├── config/
│   │   │   ├── api.config.ts      # API configuration
│   │   │   └── app.config.ts      # App configuration
│   │   ├── types/                 # TypeScript types
│   │   ├── utils/                 # Utility functions
│   │   └── styles/                # Global styles
│   ├── public/                    # Static assets
│   ├── package.json               # Node dependencies
│   ├── tsconfig.json              # TypeScript config
│   ├── tailwind.config.js         # Tailwind config
│   └── next.config.js             # Next.js config
│
├── docker-compose.yml             # Docker Compose config
├── README.md                      # This file
└── .gitignore
```

---

## 🔐 Security Features

### Authentication & Authorization
- ✅ JWT-based stateless authentication
- ✅ Bcrypt password hashing with Argon2
- ✅ Token expiration after 60 minutes
- ✅ Refresh token mechanism
- ✅ Role-based access control (RBAC)

### Attack Prevention
- ✅ CSRF token validation on all POST/PUT/DELETE
- ✅ Rate limiting (10 requests/minute per user)
- ✅ SQL injection prevention (parameterized queries)
- ✅ XSS protection (Content Security Policy headers)
- ✅ CORS validation (whitelist-based)
- ✅ HTTPS enforcement in production

### Data Protection
- ✅ Payload integrity verification (HMAC-SHA256)
- ✅ Secure password storage (Argon2)
- ✅ Encrypted sensitive data
- ✅ Audit logging of all security events
- ✅ PII handling compliance

### Webhook Security
- ✅ Signature verification
- ✅ Timeout enforcement (30 seconds)
- ✅ Payload size limits
- ✅ Retry with exponential backoff
- ✅ Dead letter queue for failed events

---

## 📊 Dashboard Features

### 📈 Main Dashboard
- **Real-time Statistics**: Live webhook event counts, success rates
- **Activity Charts**: Time-series visualization of event patterns
- **Recent Events**: Latest 100 webhook events with details
- **Provider Summary**: Status and metrics for each provider
- **Security Alerts**: Active threats and suspicious patterns
- **Export to PDF**: Download dashboard snapshot

### 👤 User Management
- **Profile Settings**: Update username, email, password
- **API Keys**: Generate and manage API tokens
- **Login History**: View recent login activity
- **Device Management**: Track active sessions

### 🔌 Provider Management
- **Add Providers**: Configure new webhook endpoints
- **Edit Configuration**: Update provider settings
- **Test Webhook**: Send test events
- **View Metrics**: Provider-specific analytics
- **Provider Analytics**: Success rates, latency, failures

### 📡 Webhook Management
- **View Events**: Inspect full webhook payloads
- **Retry Failed**: Manually retry failed events
- **Filter & Search**: Advanced filtering options
- **Export Events**: Download event data
- **Event Details**: Request/response headers and body

### 🛡️ Security & Logs
- **Security Logs**: All security-related events
- **Audit Trail**: Complete activity history
- **Threat Detection**: Suspicious pattern alerts
- **Rate Limit Status**: Current limits and usage
- **Login Attempts**: Failed and successful logins

---

## 🎯 Attack Simulator

The attack simulator tests your webhook security with 8 scenarios:

### 1. ✅ Invalid Signature
- Tampered signature (`X-Signature` header)
- **Test**: Ensures HMAC-SHA256 signature validation
- **Expected**: `Invalid webhook signature` rejection

### 2. 🔴 Replay Attack
- Same webhook sent twice with identical request ID
- **Test**: Replay detection and idempotency
- **Expected**: `Webhook already processed (replay detected)`

### 3. ⚠️ Rate Limiting Bypass
- 15 rapid webhook requests
- **Test**: Rate limit enforcement (10 requests/minute)
- **Expected**: After 7 requests, remaining blocked with countdown

### 4. 💥 Timestamp Tampering
- Webhook timestamp 10 minutes old
- **Test**: Timestamp validation window
- **Expected**: Old timestamp rejected

### 5. 📢 Payload Tampering
- Signature for original payload, but modified payload sent
- **Test**: Payload integrity verification
- **Expected**: Modified payload detected and rejected

### 6. 🔁 Missing Security Headers
- Webhook missing `X-Signature` or `X-Timestamp`
- **Test**: Required header validation
- **Expected**: Missing headers rejected

### 7. 🕐 Future Timestamp
- Webhook timestamp 1 hour in the future
- **Test**: Time-based validation bounds
- **Expected**: Future timestamp rejected

### 8. 🧬 Valid Webhook
- Properly signed webhook with valid headers
- **Test**: Baseline functionality verification
- **Expected**: Webhook accepted and processed

**Run Attack Simulator:**
```bash
cd backend
python attack_simulator.py
```

The simulator creates a test attacker user, provider, and executes all 8 scenarios in sequence, displaying detailed output for each attack and its results.

---

## 📡 API Endpoints

### Authentication
```
POST   /auth/register       # Create new account
POST   /auth/login          # Authenticate user
POST   /auth/logout         # End session
GET    /auth/me             # Get current user
POST   /auth/refresh        # Refresh token
```

### Webhooks
```
GET    /admin/webhooks              # List webhooks
POST   /admin/webhooks              # Create webhook
PUT    /admin/webhooks/{id}         # Update webhook
DELETE /admin/webhooks/{id}         # Delete webhook
GET    /admin/webhooks/stats        # Webhook statistics
GET    /admin/webhooks/events       # Event history
```

### Providers
```
GET    /admin/providers             # List providers
POST   /admin/providers             # Create provider
PUT    /admin/providers/{id}        # Update provider
DELETE /admin/providers/{id}        # Delete provider
POST   /admin/providers/{id}/test   # Test provider
```

### Logs & Analytics
```
GET    /admin/logs                  # Security logs
GET    /admin/logs/stats            # Log statistics
GET    /admin/analytics/webhooks    # Webhook analytics
GET    /admin/analytics/providers   # Provider analytics
```

### WebSocket
```
WS     /ws?token=<jwt>              # Real-time events
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. WebSocket Connection Failed
**Issue**: `WebSocket error: Connection refused`

**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Verify token is valid
# Check browser console for token details

# Restart backend
cd backend && uvicorn app.main:app --reload
```

#### 2. Login Failed (401 Unauthorized)
**Issue**: Valid credentials but login fails

**Solution:**
```bash
# Check database connection
python -c "from app.db.session import AsyncSessionLocal; print('DB OK')"

# Verify user exists
python check_users.py

# Test credentials directly
python test_specific_credentials.py "username" "password"
```

#### 3. Database Connection Error
**Issue**: `Could not connect to database`

**Solution:**
```bash
# Verify PostgreSQL is running
psql -h localhost -U postgres -d webshield

# Check connection string in .env
cat .env | grep DATABASE_URL

# Run migrations
alembic upgrade head
```

#### 4. Redis Connection Error
**Issue**: `Could not connect to Redis`

**Solution:**
```bash
# Check Redis is running
redis-cli ping

# Verify Redis URL in .env
cat .env | grep REDIS_URL

# Test connection
python -c "import redis; r = redis.from_url('redis://localhost:6380'); print(r.ping())"
```

#### 5. CORS Error
**Issue**: `Access to XMLHttpRequest blocked by CORS`

**Solution:**
```bash
# Update .env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Restart backend
```

#### 6. Rate Limit Issues
**Issue**: Getting 429 Too Many Requests

**Solution:**
```bash
# Check Redis rate limit keys
redis-cli KEYS "rate_limit:*"

# Clear rate limits
redis-cli FLUSHDB

# Increase limit in .env
RATE_LIMIT_PER_MINUTE=20
```

---

## 📊 Performance Considerations

### Database Optimization
- Connection pooling: 5-20 connections
- Query optimization with indexes
- Async/await for non-blocking operations

### Caching Strategy
- Redis for rate limiting
- Query result caching (1 hour TTL)
- WebSocket message batching

### Frontend Optimization
- React Query for automatic caching
- Code splitting with Next.js
- Image optimization
- Lazy loading of routes

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature/amazing`
5. Submit pull request

---

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [WebSocket Guide](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [OWASP Security Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Webhook Best Practices](https://www.svix.com/resources/guides/webhook-security/)

---
**Last Updated**: March 25, 2026  
**Version**: 1.0.0  
**Status**: Production Ready ✅
