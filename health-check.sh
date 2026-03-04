#!/bin/bash

# WebShield Health Check Script
# This script verifies all components are working correctly

echo "🔍 WebShield Health Check"
echo "=========================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker containers
echo "📦 Checking Docker Containers..."
if docker ps | grep -q "webshield-postgres"; then
    echo -e "${GREEN}✓${NC} PostgreSQL container is running"
else
    echo -e "${RED}✗${NC} PostgreSQL container is NOT running"
fi

if docker ps | grep -q "webshield-redis"; then
    echo -e "${GREEN}✓${NC} Redis container is running"
else
    echo -e "${RED}✗${NC} Redis container is NOT running"
fi
echo ""

# Check Backend
echo "🔧 Checking Backend API..."
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null)
if [ "$BACKEND_HEALTH" = "200" ]; then
    echo -e "${GREEN}✓${NC} Backend API is healthy (http://localhost:8000)"
    
    # Test admin endpoints
    echo "  Testing admin endpoints..."
    
    PROVIDERS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/admin/providers 2>/dev/null)
    if [ "$PROVIDERS" = "200" ]; then
        echo -e "  ${GREEN}✓${NC} Providers endpoint working"
    else
        echo -e "  ${RED}✗${NC} Providers endpoint failed (HTTP $PROVIDERS)"
    fi
    
    WEBHOOKS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/admin/webhooks 2>/dev/null)
    if [ "$WEBHOOKS" = "200" ]; then
        echo -e "  ${GREEN}✓${NC} Webhooks endpoint working"
    else
        echo -e "  ${RED}✗${NC} Webhooks endpoint failed (HTTP $WEBHOOKS)"
    fi
    
    LOGS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/admin/logs 2>/dev/null)
    if [ "$LOGS" = "200" ]; then
        echo -e "  ${GREEN}✓${NC} Security logs endpoint working"
    else
        echo -e "  ${RED}✗${NC} Security logs endpoint failed (HTTP $LOGS)"
    fi
else
    echo -e "${RED}✗${NC} Backend API is NOT responding (HTTP $BACKEND_HEALTH)"
fi
echo ""

# Check Frontend
echo "🎨 Checking Frontend..."
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null)
if [ "$FRONTEND_HEALTH" = "200" ]; then
    echo -e "${GREEN}✓${NC} Frontend is running (http://localhost:3000)"
else
    echo -e "${RED}✗${NC} Frontend is NOT responding (HTTP $FRONTEND_HEALTH)"
fi
echo ""

# Check Database Connection
echo "🗄️  Checking Database..."
DB_CHECK=$(docker exec webshield-postgres pg_isready -U webhook_user -d webhook_gateway 2>/dev/null)
if echo "$DB_CHECK" | grep -q "accepting connections"; then
    echo -e "${GREEN}✓${NC} Database is accepting connections"
else
    echo -e "${RED}✗${NC} Database connection failed"
fi
echo ""

# Check Redis Connection
echo "💾 Checking Redis..."
REDIS_CHECK=$(docker exec webshield-redis redis-cli ping 2>/dev/null)
if [ "$REDIS_CHECK" = "PONG" ]; then
    echo -e "${GREEN}✓${NC} Redis is responding"
else
    echo -e "${RED}✗${NC} Redis connection failed"
fi
echo ""

# Summary
echo "=========================="
echo "📊 Health Check Summary"
echo "=========================="
echo ""
echo "Services Status:"
echo "  • Docker Containers: Check above"
echo "  • Backend API: http://localhost:8000"
echo "  • Frontend: http://localhost:3000"
echo "  • Database: PostgreSQL on port 5434"
echo "  • Cache: Redis on port 6380"
echo ""
echo "Next Steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Navigate to Dashboard to see stats"
echo "  3. Create a provider in Providers page"
echo "  4. Send test webhooks"
echo ""
