#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

PROJECT_ROOT=~/trafic_agent
FRONTEND_DIR=$PROJECT_ROOT/admin-panel-vue-main/admin-panel-vue-main
NGINX_ROOT=/var/www/admirra.ru

echo "🚀 Starting full deployment..."

# 1. Pull latest changes from GitHub
echo "⏬ Pulling latest changes from GitHub..."
cd $PROJECT_ROOT
git pull origin main

# 2. Update Backend and Database using Docker
echo "🐳 Restarting Backend and Database..."
docker compose up -d --build backend db

# 3. Run Database Migrations
echo "🐘 Running database migrations..."
docker compose exec -T backend alembic upgrade head

# 4. Build Frontend
echo "📦 Building Frontend..."
cd $FRONTEND_DIR
npm install
npm run build

# 5. Deploy Frontend to Nginx Root
echo "📂 Copying build files to $NGINX_ROOT..."
sudo cp -r dist/* $NGINX_ROOT/

# 6. Reload Nginx
echo "⚙️ Reloading Nginx..."
sudo nginx -t && sudo systemctl reload nginx

echo "✅ Deployment completed successfully!"
