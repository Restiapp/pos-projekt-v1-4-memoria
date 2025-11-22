#!/bin/bash
echo "🌱 Quick Seed Script - Creating Essential Demo Data"
echo "=================================================="

# Wait for services
sleep 3

# RBAC seed (creates admin user)
echo "📝 Seeding RBAC (Admin user: admin/1234)..."
docker exec pos-service-admin python backend/service_admin/seed_rbac.py

echo "✅ Seeding complete!"
echo ""
echo "🎯 Login Credentials:"
echo "   Username: admin"
echo "   Password: 1234"
echo ""
echo "📍 Frontend URL: http://localhost:5173"
