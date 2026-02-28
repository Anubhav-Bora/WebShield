# Secure Webhook Gateway

A production-grade webhook gateway with HMAC verification, rate limiting, replay protection, and comprehensive security monitoring.

## Features

✅ **HMAC SHA256 Signature Verification** - Validates webhook authenticity with constant-time comparison  
✅ **Timestamp Validation** - Prevents old/future timestamp attacks (5-minute window)  
✅ **Replay Protection** - Detects and prevents duplicate webhook processing  
✅ **Rate Limiting** - Token bucket algorithm (100 req/60s per provider)  
✅ **Security Event Logging** - Tracks all security violations and suspicious activity  
✅ **Async Webhook Forwarding** - Non-blocking webhook delivery to internal services  
✅ **Professional Dashboard** - Real-time monitoring and management UI  
✅ **RESTful API** - Complete admin API for provider and webhook management  

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **Redis** - In-memory cache for rate limiting and replay protection
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation

### Frontend
- **Next.js 16** - React framework with TypeScript
- **React Query** - Server state management
- **Zustand** - Client state management
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/webhook-gateway.git
cd webhook-gateway
```

2. **Start Docker services**
```bash
docker-compose up -d
```

3. **Setup Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\Activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

4. **Setup Frontend**
```bash
cd frontend
npm install
```

5. **Run Backend**
```bash
cd backend
venv\Scripts\Activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Run Frontend** (in a new terminal)
```bash
cd frontend
npm run dev
```

7. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Configuration

### Backend Environment Variables
Create `backend/.env`:
```
DATABASE_URL=postgresql+asyncpg://webshield:webshield_password@localhost:5434/webshield_db
REDIS_URL=redis://localhost:6380/0
JWT_SECRET_KEY=your-secret-key
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
REPLAY_PROTECTION_WINDOW_SECONDS=300
FORWARDING_TIMEOUT_SECONDS=10
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend Environment Variables
Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Endpoints

### Webhook Ingestion
- `POST /webhooks/{provider_name}` - Receive and process webhooks

### Provider Management
- `GET /admin/providers` - List all providers
- `POST /admin/providers` - Create provider
- `GET /admin/providers/{name}` - Get provider details
- `PUT /admin/providers/{name}` - Update provider
- `DELETE /admin/providers/{name}` - Delete provider
- `GET /admin/providers/{name}/stats` - Get provider statistics

### Webhook Management
- `GET /admin/webhooks` - List webhook events
- `GET /admin/webhooks/{id}` - Get webhook details
- `GET /admin/webhooks/stats` - Get webhook statistics
- `POST /admin/webhooks/{id}/retry` - Retry failed webhook

### Security Logs
- `GET /admin/logs` - List security logs
- `GET /admin/logs/{id}` - Get security log details
- `GET /admin/logs/stats` - Get security statistics
- `GET /admin/logs/export` - Export logs as CSV

### Health
- `GET /health` - Health check
- `GET /` - API information

## Project Structure

```
webhook-gateway/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # API endpoints
│   │   ├── core/                # Core utilities
│   │   ├── db/                  # Database models
│   │   ├── schemas/             # Pydantic schemas
│   │   └── main.py              # FastAPI app
│   ├── alembic/                 # Database migrations
│   ├── requirements.txt          # Python dependencies
│   └── .env                      # Environment variables (not in git)
│
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js pages
│   │   ├── services/            # API services
│   │   ├── hooks/               # Custom hooks
│   │   ├── store/               # Zustand stores
│   │   ├── types/               # TypeScript types
│   │   ├── utils/               # Utilities
│   │   └── config/              # Configuration
│   ├── package.json             # Node dependencies
│   └── .env.local               # Environment variables (not in git)
│
├── docker-compose.yml           # Docker services
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Documentation

- **[BACKEND_FRONTEND_VERIFICATION_REPORT.md](./BACKEND_FRONTEND_VERIFICATION_REPORT.md)** - Comprehensive alignment and verification report
- **[ALIGNMENT_SUMMARY.md](./ALIGNMENT_SUMMARY.md)** - Quick alignment summary
- **[SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md)** - Complete system architecture
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Quick reference guide

## Security Features

### Signature Verification
- HMAC-SHA256 signature verification
- Constant-time comparison (prevents timing attacks)
- Validates webhook authenticity

### Timestamp Validation
- 5-minute window (configurable)
- Prevents old/future timestamp attacks

### Replay Protection
- Request ID deduplication via Redis
- 5-minute window (configurable)
- Prevents duplicate webhook processing

### Rate Limiting
- Token bucket algorithm
- 100 requests/60 seconds per provider (configurable)
- Returns remaining requests in response

### Security Event Logging
- Logs all security violations
- Tracks: invalid signatures, replay attempts, rate limit violations, timestamp errors
- Enables threat detection and analysis

## Database Schema

### Providers
```sql
CREATE TABLE providers (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    secret_key VARCHAR(500) NOT NULL,
    forwarding_url VARCHAR(500) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);
```

### Webhook Events
```sql
CREATE TABLE webhook_events (
    id UUID PRIMARY KEY,
    provider_id UUID NOT NULL REFERENCES providers(id),
    request_id VARCHAR(255) UNIQUE NOT NULL,
    payload JSONB NOT NULL,
    headers JSONB NOT NULL,
    signature_valid BOOLEAN NOT NULL,
    forwarded BOOLEAN DEFAULT false,
    response_status INTEGER,
    response_body TEXT,
    error_message TEXT,
    received_at TIMESTAMP DEFAULT now(),
    forwarded_at TIMESTAMP
);
```

### Security Logs
```sql
CREATE TABLE security_logs (
    id UUID PRIMARY KEY,
    provider_name VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    request_id VARCHAR(255),
    details JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);
```

## Testing

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm test
```

## Deployment

### Production Build

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run build
npm start
```

### Docker Deployment
```bash
docker-compose -f docker-compose.yml up -d
```

## Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify DATABASE_URL and REDIS_URL in .env
- Ensure PostgreSQL and Redis are running

### Frontend won't start
- Check if port 3000 is available
- Verify NEXT_PUBLIC_API_URL in .env.local
- Clear node_modules and reinstall: `npm install`

### Database connection issues
- Verify PostgreSQL is running: `docker-compose ps`
- Check credentials in DATABASE_URL
- Ensure database exists

### Redis connection issues
- Verify Redis is running: `docker-compose ps`
- Check REDIS_URL in .env
- Test connection: `redis-cli -p 6380 ping`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or suggestions:
1. Check the [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) for common tasks
2. Review the [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) for architecture details
3. Check API documentation at http://localhost:8000/docs
4. Open an issue on GitHub

## Roadmap

- [ ] JWT authentication
- [ ] User management
- [ ] Webhook templates
- [ ] Advanced filtering and search
- [ ] Real-time notifications via WebSocket
- [ ] Webhook replay functionality
- [ ] Custom header support
- [ ] Webhook transformation rules
- [ ] Analytics dashboard
- [ ] Multi-tenant support

## Authors

- **Kiro AI Assistant** - Initial development

## Acknowledgments

- FastAPI for the excellent web framework
- Next.js for the React framework
- PostgreSQL for the reliable database
- Redis for the in-memory cache

---

**Status:** ✅ Production-Ready  
**Version:** 1.0.0  
**Last Updated:** February 28, 2026
