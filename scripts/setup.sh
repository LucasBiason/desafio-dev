#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

COMPOSE="docker compose"

echo -e "${CYAN}=== CNAB Parser Setup ===${NC}"
echo ""

echo -e "${CYAN}[1/6] Building and starting containers...${NC}"
$COMPOSE up --build -d
echo -e "${GREEN}Containers started.${NC}"
echo ""

echo -e "${CYAN}[2/6] Waiting for database...${NC}"
until $COMPOSE exec db pg_isready -U cnab > /dev/null 2>&1; do
  sleep 1
done
echo -e "${GREEN}Database is ready.${NC}"
echo ""

echo -e "${CYAN}[3/6] Waiting for services...${NC}"
sleep 10
echo -e "${GREEN}Services are up.${NC}"
echo ""

echo -e "${CYAN}[4/6] Applying migrations...${NC}"
$COMPOSE exec user-service /entrypoint.sh migrate
$COMPOSE exec cnab-service /entrypoint.sh migrate
$COMPOSE exec upload-service /entrypoint.sh migrate
echo -e "${GREEN}All migrations applied.${NC}"
echo ""

echo -e "${CYAN}[5/6] Creating admin user...${NC}"
$COMPOSE exec user-service python manage.py shell -c "
from users.models.user import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(username='admin', email='admin@cnabparser.dev', password='admin123')
    print('Admin user created (admin / admin123)')
else:
    print('Admin user already exists.')
"
echo ""

echo -e "${CYAN}[6/6] Verifying services...${NC}"
sleep 3
echo -e "${GREEN}=== Setup complete ===${NC}"
echo ""
echo "  Frontend:          http://localhost:7000"
echo "  User Service:      http://localhost:7001"
echo "  CNAB Service:      http://localhost:7002"
echo "  Upload Service:    http://localhost:7003"
echo "  Dashboard Service: http://localhost:7004"
echo "  Swagger:           http://localhost:7001/swagger/"
echo ""
echo "  Login: admin / admin123"
echo ""
