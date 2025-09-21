#!/bin/bash

# NOV-RECO Quick Setup Script for Python 3.6
# Simple one-command setup

echo "🚀 NOV-RECO Quick Setup Starting..."

# Install pip3
curl -s https://bootstrap.pypa.io/pip/3.6/get-pip.py -o get-pip.py
python3 get-pip.py --user --quiet
export PATH="$HOME/.local/bin:$PATH"

# Create venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Install packages
python -m pip install --upgrade "pip<21.0" --quiet

cat > requirements-py36.txt << 'EOF'
Django==3.2.25
django-allauth==0.54.0
djangorestframework==3.14.0
Pillow==8.4.0
python-dotenv==0.19.2
EOF

pip install -r requirements-py36.txt --quiet

# Setup Django
mkdir -p data logs media staticfiles
export DJANGO_ENVIRONMENT=test
export DATABASE_NAME=data/db_test.sqlite3
export ALLOWED_HOSTS="checkin.taylaibui.vn,localhost,127.0.0.1,0.0.0.0"

python manage.py migrate --verbosity=0
python manage.py collectstatic --noinput --verbosity=0

# Create admin user
python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin created: admin/admin123')
PYEOF

echo "✅ Setup completed!"
echo "🚀 Start server: source venv/bin/activate && python manage.py runserver 0.0.0.0:8000"
