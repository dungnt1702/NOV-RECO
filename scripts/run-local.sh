#!/bin/bash
# Local Development Runner

# Set local environment variables
export DJANGO_ENVIRONMENT=local
export DJANGO_DEBUG=1
export DJANGO_SECRET_KEY=dev-secret-key-change-me
export DATABASE_ENGINE=django.db.backends.sqlite3
export DATABASE_NAME=data/db.sqlite3
export ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
export SERVER_PORT=3000

echo "🚀 Starting NOV-RECO Check-in System (Local Development)"
echo "📍 Environment: $DJANGO_ENVIRONMENT"
echo "🐛 Debug mode: $DJANGO_DEBUG"
echo "🌐 Server will run on: http://localhost:$SERVER_PORT"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Start development server
echo "🚀 Starting development server..."
python manage.py runserver $SERVER_PORT
