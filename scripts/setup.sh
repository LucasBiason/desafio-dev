#!/usr/bin/env bash
set -euo pipefail

# ============================================
# CNAB Parser — Full environment setup
# ============================================
# Usage: ./scripts/setup.sh
# Creates databases, applies migrations, seeds data, creates admin user.

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
NC='\033[0m'

COMPOSE="docker compose"

echo -e "${CYAN}=== CNAB Parser Setup ===${NC}"
echo ""

# 1. Build and start infrastructure
echo -e "${CYAN}[1/6] Building and starting containers...${NC}"
$COMPOSE up --build -d
echo -e "${GREEN}Containers started.${NC}"
echo ""

# 2. Wait for database to be ready
echo -e "${CYAN}[2/6] Waiting for database...${NC}"
until $COMPOSE exec db pg_isready -U cnab > /dev/null 2>&1; do
  sleep 1
done
echo -e "${GREEN}Database is ready.${NC}"
echo ""

# 3. Wait for services to be healthy
echo -e "${CYAN}[3/6] Waiting for services to be healthy...${NC}"
sleep 5
echo -e "${GREEN}Services are up.${NC}"
echo ""

# 4. Apply user-service migrations (Django)
echo -e "${CYAN}[4/6] Applying user-service migrations...${NC}"
$COMPOSE exec user-service /entrypoint.sh migrate
echo -e "${GREEN}User-service migrations applied.${NC}"
echo ""

# 5. Apply cnab-service migrations (SQL + seed)
echo -e "${CYAN}[5/7] Applying cnab-service migrations...${NC}"
$COMPOSE exec cnab-service /entrypoint.sh migrate
echo -e "${GREEN}CNAB-service migrations applied.${NC}"
echo ""

# 5b. Apply upload-service migrations
echo -e "${CYAN}[5b/7] Applying upload-service migrations...${NC}"
$COMPOSE exec upload-service /entrypoint.sh migrate
echo -e "${GREEN}Upload-service migrations applied.${NC}"
echo ""

# 6. Create admin superuser
echo -e "${CYAN}[6/7] Creating admin user...${NC}"
$COMPOSE exec user-service python manage.py shell -c "
from users.models.user import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(username='admin', email='admin@cnabparser.dev', password='admin123')
    print('Admin user created (admin / admin123)')
else:
    print('Admin user already exists.')
"
echo ""

# Done
echo -e "${GREEN}=== Setup complete ===${NC}"
echo ""
echo "  Frontend:       http://localhost:7000"
echo "  User Service:   http://localhost:7001"
echo "  CNAB Service:   http://localhost:7002"
echo "  Upload Service: http://localhost:7003"
echo "  Swagger:        http://localhost:7001/swagger/"
echo ""
echo "  Login: admin / admin123"
echo ""
