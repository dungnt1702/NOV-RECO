# Development Guide

## 🏗️ Project Structure

```
checkin_project/
├── checkin/                 # Main app
│   ├── models.py           # Database models
│   ├── views.py            # View controllers
│   ├── urls.py             # URL routing
│   ├── serializers.py      # API serializers
│   ├── management/         # Custom commands
│   └── migrations/         # Database migrations
├── users/                  # User management app
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── data/                   # Data and scripts
├── docs/                   # Documentation
└── project/                # Django settings
```

## 🔧 Development Setup

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data
python manage.py create_sample_users
python manage.py create_sample_areas
```

### 3. Development Server
```bash
# Start development server
python manage.py runserver

# With custom port
python manage.py runserver 127.0.0.1:3000
```

## 🛠️ Custom Commands

### Available Commands
```bash
# User management
python manage.py create_admin
python manage.py create_sample_users
python manage.py setup_user_groups

# Data management
python manage.py create_sample_areas
python manage.py create_sample_data

# Database utilities
python manage.py view_database
python manage.py update_checkin_areas
```

## 📊 Models

### User Model
```python
class User(AbstractUser):
    role = models.CharField(max_length=20, choices=UserRole.choices)
    employee_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
```

### Checkin Model
```python
class Checkin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    checkin_time = models.DateTimeField()
    checkout_time = models.DateTimeField(null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='checkins/', blank=True)
```

### Area Model
```python
class Area(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    radius = models.IntegerField(default=100)  # meters
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/user/` - Get current user

### Checkin
- `GET /api/checkins/` - List checkins
- `POST /api/checkins/` - Create checkin
- `PUT /api/checkins/{id}/` - Update checkin
- `DELETE /api/checkins/{id}/` - Delete checkin

### Areas
- `GET /api/areas/` - List areas
- `POST /api/areas/` - Create area
- `PUT /api/areas/{id}/` - Update area
- `DELETE /api/areas/{id}/` - Delete area

### Users
- `GET /api/users/` - List users
- `POST /api/users/` - Create user
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test checkin
python manage.py test users

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Structure
```
tests/
├── test_models.py
├── test_views.py
├── test_serializers.py
└── test_utils.py
```

## 🚀 Deployment

### Production Settings
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = 'your-production-secret-key'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nov_reco_db',
        'USER': 'db_user',
        'PASSWORD': 'db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Environment Variables
```env
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/db
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput

# Serve with nginx/apache
# Configure media files serving
```

## 🔍 Debugging

### Debug Mode
```python
# settings.py
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Common Issues
1. **Port already in use**: Kill existing process or use different port
2. **Database locked**: Check if another process is using the database
3. **Static files not loading**: Run `collectstatic` command
4. **Permission errors**: Check file permissions and ownership

## 📝 Code Style

### Python
- Follow PEP 8
- Use type hints where possible
- Write docstrings for functions and classes
- Keep functions small and focused

### Django
- Use class-based views when appropriate
- Follow Django naming conventions
- Use Django's built-in security features
- Write tests for all functionality

### Frontend
- Use semantic HTML
- Follow BEM CSS methodology
- Use modern JavaScript (ES6+)
- Ensure responsive design
