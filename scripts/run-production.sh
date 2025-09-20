#!/bin/bash
# Production Runner (for manual testing)

# Load production environment variables
if [ -f "config/production.env" ]; then
    export $(grep -v '^#' config/production.env | xargs)
fi

# Override some settings for manual production testing
export DJANGO_ENVIRONMENT=production
export DJANGO_DEBUG=0

echo "🚀 Starting NOV-RECO Check-in System (Production Mode)"
echo "📍 Environment: $DJANGO_ENVIRONMENT"
echo "🐛 Debug mode: $DJANGO_DEBUG"
echo "🌐 Server will run on: http://localhost:8000"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install production dependencies
echo "📦 Installing production dependencies..."
pip install -r requirements-production.txt

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create logs directory
mkdir -p logs

# Start production server with Gunicorn
echo "🚀 Starting production server with Gunicorn..."
gunicorn --workers 3 --bind 0.0.0.0:8000 project.wsgi:application
